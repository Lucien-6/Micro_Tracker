"""
SAM2混合提示处理单元测试

测试修复后的process_video_with_refinement函数是否正确处理各种提示组合

Author: Lucien (lucien-6@qq.com)
Date: 2025-11-01
"""

import sys
import os
import unittest
from unittest.mock import Mock, MagicMock, patch, call
import numpy as np
import torch

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestMixedPromptsHandling(unittest.TestCase):
    """测试混合提示处理的正确性"""
    
    def setUp(self):
        """每个测试前的准备工作"""
        # 创建mock对象
        self.mock_args = Mock()
        self.mock_args.video_path = "test_video.mp4"
        self.mock_args.model_path = "test_model.pt"
        self.mock_args.device = "cpu"
        self.mock_args.video_output_path = "output.mp4"
        self.mock_args.mask_dir = None
        self.mock_args.save_to_video = False
        self.mock_args.progress_callback = None
        
        # 记录add_new_points_or_box的调用
        self.api_calls = []
        
    def _create_mock_predictor(self):
        """创建mock SAM2 predictor"""
        mock_predictor = MagicMock()
        
        # Mock init_state
        mock_state = {"test": "state"}
        mock_predictor.init_state.return_value = mock_state
        
        # Mock add_new_points_or_box - 记录调用参数
        def record_call(**kwargs):
            self.api_calls.append(kwargs)
            # 返回模拟的输出
            mock_logits = torch.zeros((1, 1, 256, 256))
            return None, [kwargs.get('obj_id', 0)], mock_logits
        
        mock_predictor.add_new_points_or_box = Mock(side_effect=record_call)
        
        # Mock propagate_in_video - 返回空迭代器
        mock_predictor.propagate_in_video.return_value = iter([])
        
        return mock_predictor, mock_state
    
    @patch('sam2.build_sam.build_sam2_video_predictor')
    @patch('cv2.VideoCapture')
    @patch('utils.utils.determine_model_cfg')
    def test_only_box_prompt(self, mock_cfg, mock_cap, mock_builder):
        """测试用例1：只有box的情况"""
        from scripts.process_video_multiframe import process_video_with_refinement
        
        # 设置mocks
        mock_cfg.return_value = "test_cfg"
        mock_predictor, mock_state = self._create_mock_predictor()
        mock_builder.return_value = mock_predictor
        
        # Mock cv2.VideoCapture
        mock_video = MagicMock()
        mock_video.get.side_effect = lambda x: {
            7: 100,  # total frames
            5: 30.0  # fps
        }.get(x, 0)
        mock_cap.return_value = mock_video
        
        # 测试数据：只有box
        annotations = {
            0: {
                1: {"box": [100, 100, 200, 200], "points": [], "labels": []}
            }
        }
        
        # 执行
        self.api_calls.clear()
        process_video_with_refinement(self.mock_args, annotations)
        
        # 验证：应该有1次API调用
        self.assertEqual(len(self.api_calls), 1, "应该只调用一次add_new_points_or_box")
        
        # 验证调用参数
        call_kwargs = self.api_calls[0]
        self.assertIn("box", call_kwargs, "应该包含box参数")
        self.assertNotIn("points", call_kwargs, "不应该包含points参数")
        self.assertEqual(call_kwargs["clear_old_points"], True, "应该使用clear_old_points=True")
        self.assertEqual(call_kwargs["obj_id"], 1, "对象ID应该为1")
        
        print("✓ 测试用例1通过：只有box的情况")
    
    @patch('sam2.build_sam.build_sam2_video_predictor')
    @patch('cv2.VideoCapture')
    @patch('utils.utils.determine_model_cfg')
    def test_only_points_prompt(self, mock_cfg, mock_cap, mock_builder):
        """测试用例2：只有points的情况"""
        from scripts.process_video_multiframe import process_video_with_refinement
        
        # 设置mocks
        mock_cfg.return_value = "test_cfg"
        mock_predictor, mock_state = self._create_mock_predictor()
        mock_builder.return_value = mock_predictor
        
        mock_video = MagicMock()
        mock_video.get.side_effect = lambda x: {7: 100, 5: 30.0}.get(x, 0)
        mock_cap.return_value = mock_video
        
        # 测试数据：只有points
        annotations = {
            0: {
                1: {"box": None, "points": [(150, 150)], "labels": [1]}
            }
        }
        
        # 执行
        self.api_calls.clear()
        process_video_with_refinement(self.mock_args, annotations)
        
        # 验证
        self.assertEqual(len(self.api_calls), 1, "应该只调用一次add_new_points_or_box")
        
        call_kwargs = self.api_calls[0]
        self.assertNotIn("box", call_kwargs, "不应该包含box参数")
        self.assertIn("points", call_kwargs, "应该包含points参数")
        self.assertIn("labels", call_kwargs, "应该包含labels参数")
        self.assertEqual(call_kwargs["clear_old_points"], True, "应该使用clear_old_points=True")
        
        print("✓ 测试用例2通过：只有points的情况")
    
    @patch('sam2.build_sam.build_sam2_video_predictor')
    @patch('cv2.VideoCapture')
    @patch('utils.utils.determine_model_cfg')
    def test_mixed_box_and_points(self, mock_cfg, mock_cap, mock_builder):
        """测试用例3：box + points混合（关键测试）"""
        from scripts.process_video_multiframe import process_video_with_refinement
        
        # 设置mocks
        mock_cfg.return_value = "test_cfg"
        mock_predictor, mock_state = self._create_mock_predictor()
        mock_builder.return_value = mock_predictor
        
        mock_video = MagicMock()
        mock_video.get.side_effect = lambda x: {7: 100, 5: 30.0}.get(x, 0)
        mock_cap.return_value = mock_video
        
        # 测试数据：box + points混合
        annotations = {
            0: {
                1: {
                    "box": [100, 100, 200, 200],
                    "points": [(150, 150), (180, 120)],
                    "labels": [1, 0]  # 一个正向点，一个负向点
                }
            }
        }
        
        # 执行
        self.api_calls.clear()
        process_video_with_refinement(self.mock_args, annotations)
        
        # ===  关键验证：应该只调用一次API ===
        self.assertEqual(len(self.api_calls), 1, 
                        "混合提示应该只调用一次add_new_points_or_box（这是修复的核心）")
        
        # 验证调用参数
        call_kwargs = self.api_calls[0]
        self.assertIn("box", call_kwargs, "应该包含box参数")
        self.assertIn("points", call_kwargs, "应该包含points参数")
        self.assertIn("labels", call_kwargs, "应该包含labels参数")
        self.assertEqual(call_kwargs["clear_old_points"], True, 
                        "应该使用clear_old_points=True（符合SAM2官方规范）")
        
        # 验证box值
        self.assertEqual(list(call_kwargs["box"]), [100, 100, 200, 200], "box坐标应该正确")
        
        # 验证points值
        points_array = call_kwargs["points"]
        self.assertEqual(len(points_array), 2, "应该有2个点击")
        
        # 验证labels值
        labels_array = call_kwargs["labels"]
        self.assertEqual(len(labels_array), 2, "应该有2个标签")
        self.assertEqual(list(labels_array), [1, 0], "标签应该为[1, 0]")
        
        print("✓ 测试用例3通过：box + points混合（一次性调用）")
    
    @patch('sam2.build_sam.build_sam2_video_predictor')
    @patch('cv2.VideoCapture')
    @patch('utils.utils.determine_model_cfg')
    def test_multi_object_multi_frame(self, mock_cfg, mock_cap, mock_builder):
        """测试用例4：多对象、多帧、混合提示"""
        from scripts.process_video_multiframe import process_video_with_refinement
        
        # 设置mocks
        mock_cfg.return_value = "test_cfg"
        mock_predictor, mock_state = self._create_mock_predictor()
        mock_builder.return_value = mock_predictor
        
        mock_video = MagicMock()
        mock_video.get.side_effect = lambda x: {7: 200, 5: 30.0}.get(x, 0)
        mock_cap.return_value = mock_video
        
        # 测试数据：多对象、多帧
        annotations = {
            0: {
                1: {"box": [50, 50, 150, 150], "points": [(100, 100)], "labels": [1]},
                2: {"box": None, "points": [(300, 300)], "labels": [1]}
            },
            50: {
                1: {"box": [60, 60, 160, 160], "points": [(110, 110), (90, 90)], "labels": [1, 0]}
            }
        }
        
        # 执行
        self.api_calls.clear()
        process_video_with_refinement(self.mock_args, annotations)
        
        # 验证：应该有3次API调用（frame 0有2个对象，frame 50有1个对象）
        self.assertEqual(len(self.api_calls), 3, "应该有3次API调用")
        
        # 验证第一帧的两个对象
        frame0_calls = [c for c in self.api_calls if c["frame_idx"] == 0]
        self.assertEqual(len(frame0_calls), 2, "第0帧应该有2个对象")
        
        # 验证第50帧的对象
        frame50_calls = [c for c in self.api_calls if c["frame_idx"] == 50]
        self.assertEqual(len(frame50_calls), 1, "第50帧应该有1个对象")
        
        # 验证frame 50的混合提示（box + 2个points）
        frame50_call = frame50_calls[0]
        self.assertIn("box", frame50_call, "第50帧应该有box")
        self.assertIn("points", frame50_call, "第50帧应该有points")
        self.assertEqual(len(frame50_call["points"]), 2, "第50帧应该有2个点击")
        
        print("✓ 测试用例4通过：多对象、多帧")
    
    @patch('sam2.build_sam.build_sam2_video_predictor')
    @patch('cv2.VideoCapture')
    @patch('utils.utils.determine_model_cfg')
    def test_empty_prompt(self, mock_cfg, mock_cap, mock_builder):
        """测试用例5：空提示（边界情况）"""
        from scripts.process_video_multiframe import process_video_with_refinement
        
        # 设置mocks
        mock_cfg.return_value = "test_cfg"
        mock_predictor, mock_state = self._create_mock_predictor()
        mock_builder.return_value = mock_predictor
        
        mock_video = MagicMock()
        mock_video.get.side_effect = lambda x: {7: 100, 5: 30.0}.get(x, 0)
        mock_cap.return_value = mock_video
        
        # 测试数据：空提示
        annotations = {
            0: {
                1: {"box": None, "points": [], "labels": []}
            }
        }
        
        # 添加progress_callback来捕获警告
        warnings = []
        self.mock_args.progress_callback = lambda msg, *args: warnings.append(msg) if "警告" in msg or "⚠️" in msg else None
        
        # 执行
        self.api_calls.clear()
        process_video_with_refinement(self.mock_args, annotations)
        
        # 验证：不应该调用API
        self.assertEqual(len(self.api_calls), 0, "空提示不应该调用add_new_points_or_box")
        
        # 验证：应该有警告日志
        self.assertTrue(any("没有任何提示" in w for w in warnings), 
                       "应该记录警告：对象没有任何提示")
        
        print("✓ 测试用例5通过：空提示被正确跳过")


class TestAPICallParameters(unittest.TestCase):
    """测试API调用参数的正确性"""
    
    @patch('sam2.build_sam.build_sam2_video_predictor')
    @patch('cv2.VideoCapture')
    @patch('utils.utils.determine_model_cfg')
    def test_clear_old_points_always_true(self, mock_cfg, mock_cap, mock_builder):
        """验证clear_old_points始终为True（符合SAM2规范）"""
        from scripts.process_video_multiframe import process_video_with_refinement
        
        # 设置mocks
        mock_cfg.return_value = "test_cfg"
        mock_predictor = MagicMock()
        mock_state = {"test": "state"}
        mock_predictor.init_state.return_value = mock_state
        
        api_calls = []
        def record_call(**kwargs):
            api_calls.append(kwargs)
            return None, [kwargs.get('obj_id', 0)], torch.zeros((1, 1, 256, 256))
        
        mock_predictor.add_new_points_or_box = Mock(side_effect=record_call)
        mock_predictor.propagate_in_video.return_value = iter([])
        mock_builder.return_value = mock_predictor
        
        mock_video = MagicMock()
        mock_video.get.side_effect = lambda x: {7: 100, 5: 30.0}.get(x, 0)
        mock_cap.return_value = mock_video
        
        # 测试多种提示组合
        annotations = {
            0: {"box": [100, 100, 200, 200], "points": [], "labels": []},  # 只有box
            1: {"box": None, "points": [(150, 150)], "labels": [1]},      # 只有points
            2: {"box": [100, 100, 200, 200], "points": [(150, 150)], "labels": [1]}  # 混合
        }
        
        # 转换为正确格式
        formatted_annotations = {
            frame_idx: {1: data} 
            for frame_idx, data in annotations.items()
        }
        
        mock_args = Mock()
        mock_args.video_path = "test.mp4"
        mock_args.model_path = "test_model.pt"
        mock_args.device = "cpu"
        mock_args.video_output_path = "output.mp4"
        mock_args.mask_dir = None
        mock_args.save_to_video = False
        mock_args.progress_callback = None
        
        # 执行
        process_video_with_refinement(mock_args, formatted_annotations)
        
        # 验证：所有调用都使用clear_old_points=True
        for call_kwargs in api_calls:
            self.assertEqual(call_kwargs["clear_old_points"], True,
                           f"所有API调用都应该使用clear_old_points=True（帧{call_kwargs['frame_idx']}）")
        
        print("✓ 参数测试通过：clear_old_points始终为True")


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestMixedPromptsHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestAPICallParameters))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出统计
    print("\n" + "="*70)
    print("测试统计：")
    print(f"  总计: {result.testsRun} 个测试")
    print(f"  ✓ 成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  ✗ 失败: {len(result.failures)}")
    print(f"  ⚠ 错误: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

