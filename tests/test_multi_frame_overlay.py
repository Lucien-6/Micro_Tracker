"""
Phase 1 MVP: 多帧标注功能单元测试

测试OverlayLayer的多帧模式功能
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from micro_tracker.components.video_widgets import OverlayLayer


def test_multi_frame_mode_initialization():
    """测试多帧模式初始化"""
    overlay = OverlayLayer()
    assert overlay.multi_frame_mode == True
    assert overlay.current_frame_idx == 0
    assert len(overlay.bboxes_per_frame) == 0
    assert overlay.bboxes == []
    print("✓ 多帧模式初始化测试通过")


def test_add_bbox_to_different_frames():
    """测试在不同帧添加边界框"""
    overlay = OverlayLayer()
    
    # 在第0帧添加
    overlay.current_frame_idx = 0
    overlay.bboxes = [[10, 10, 100, 100, 0]]
    overlay._sync_bboxes_to_current_frame()
    
    # 切换到第5帧添加
    overlay.current_frame_idx = 5
    overlay._sync_bboxes_from_current_frame()
    assert len(overlay.bboxes) == 0, "第5帧应该是空的"
    
    overlay.bboxes = [[20, 20, 120, 120, 1]]
    overlay._sync_bboxes_to_current_frame()
    
    # 验证数据
    assert len(overlay.bboxes_per_frame) == 2
    assert 0 in overlay.bboxes_per_frame
    assert 5 in overlay.bboxes_per_frame
    assert len(overlay.bboxes_per_frame[0]) == 1
    assert len(overlay.bboxes_per_frame[5]) == 1
    print("✓ 不同帧添加边界框测试通过")


def test_frame_switch_updates_bboxes():
    """测试帧切换时边界框正确更新"""
    overlay = OverlayLayer()
    
    # 设置第0帧
    overlay.bboxes_per_frame[0] = [[10, 10, 100, 100, 0]]
    # 设置第10帧
    overlay.bboxes_per_frame[10] = [[20, 20, 120, 120, 1], [30, 30, 130, 130, 2]]
    
    # 切换到第0帧
    overlay.set_current_frame(0)
    assert len(overlay.bboxes) == 1, f"第0帧应该有1个边界框，实际: {len(overlay.bboxes)}"
    
    # 切换到第10帧
    overlay.set_current_frame(10)
    assert len(overlay.bboxes) == 2, f"第10帧应该有2个边界框，实际: {len(overlay.bboxes)}"
    
    # 切换到第5帧（空帧）
    overlay.set_current_frame(5)
    assert len(overlay.bboxes) == 0, f"第5帧应该为空，实际: {len(overlay.bboxes)}"
    print("✓ 帧切换更新边界框测试通过")


def test_backward_compatibility():
    """测试向后兼容性"""
    overlay = OverlayLayer()
    
    # 模拟旧代码直接设置bboxes
    overlay.multi_frame_mode = False
    overlay.bboxes = [[10, 10, 100, 100, 0]]
    
    # 获取标注应该返回单帧格式
    annotations = overlay.get_all_annotations()
    assert 0 in annotations, "向后兼容模式应返回第0帧"
    assert len(annotations[0]) == 1
    print("✓ 向后兼容性测试通过")


def test_get_annotated_frame_indices():
    """测试获取已标注帧索引列表"""
    overlay = OverlayLayer()
    
    # 添加多个帧的标注
    overlay.bboxes_per_frame[0] = [[10, 10, 100, 100, 0]]
    overlay.bboxes_per_frame[15] = [[20, 20, 120, 120, 1]]
    overlay.bboxes_per_frame[42] = [[30, 30, 130, 130, 2]]
    
    indices = overlay.get_annotated_frame_indices()
    assert indices == [0, 15, 42], f"期望 [0, 15, 42]，实际: {indices}"
    print("✓ 获取已标注帧索引测试通过")


def test_get_annotation_count():
    """测试获取当前帧标注数量"""
    overlay = OverlayLayer()
    
    overlay.bboxes_per_frame[0] = [[10, 10, 100, 100, 0], [20, 20, 120, 120, 1]]
    overlay.bboxes_per_frame[5] = [[30, 30, 130, 130, 2]]
    
    # 切换到第0帧
    overlay.set_current_frame(0)
    assert overlay.get_annotation_count() == 2
    
    # 切换到第5帧
    overlay.set_current_frame(5)
    assert overlay.get_annotation_count() == 1
    
    # 切换到空帧
    overlay.set_current_frame(10)
    assert overlay.get_annotation_count() == 0
    print("✓ 获取标注数量测试通过")


def test_delete_bbox_syncs_correctly():
    """测试删除边界框正确同步"""
    overlay = OverlayLayer()
    
    # 在第0帧添加2个边界框
    overlay.current_frame_idx = 0
    overlay.bboxes = [[10, 10, 100, 100, 0], [20, 20, 120, 120, 1]]
    overlay._sync_bboxes_to_current_frame()
    
    # 删除一个
    overlay.selected_bbox = 0
    overlay.delete_selected_bbox()
    
    # 验证字典也更新了
    assert len(overlay.bboxes_per_frame[0]) == 1
    print("✓ 删除边界框同步测试通过")


def test_clear_bboxes_syncs_correctly():
    """测试清除边界框正确同步"""
    overlay = OverlayLayer()
    
    # 在第0帧添加边界框
    overlay.current_frame_idx = 0
    overlay.bboxes = [[10, 10, 100, 100, 0]]
    overlay._sync_bboxes_to_current_frame()
    
    # 清除
    overlay.clear_bboxes()
    
    # 验证字典也清空了
    assert 0 not in overlay.bboxes_per_frame
    print("✓ 清除边界框同步测试通过")


if __name__ == "__main__":
    """运行所有测试"""
    print("\n" + "="*60)
    print("Phase 1 MVP: 多帧标注功能测试")
    print("="*60 + "\n")
    
    try:
        test_multi_frame_mode_initialization()
        test_add_bbox_to_different_frames()
        test_frame_switch_updates_bboxes()
        test_backward_compatibility()
        test_get_annotated_frame_indices()
        test_get_annotation_count()
        test_delete_bbox_syncs_correctly()
        test_clear_bboxes_syncs_correctly()
        
        print("\n" + "="*60)
        print("✓✓✓ 所有测试通过！ ✓✓✓")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

