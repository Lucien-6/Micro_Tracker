"""
测试 bbox_process 函数是否正确处理新的5值格式
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.utils import bbox_process


def test_bbox_process_4_values():
    """测试4值格式（旧格式）"""
    bbox_list = [
        [10, 20, 110, 120],
        [30, 40, 130, 140]
    ]
    
    prompts = bbox_process(bbox_list)
    
    assert len(prompts) == 2
    assert 0 in prompts
    assert 1 in prompts
    assert prompts[0] == ((10, 20, 110, 120), "obj_0")
    assert prompts[1] == ((30, 40, 130, 140), "obj_1")
    print("✓ 4值格式测试通过")


def test_bbox_process_5_values():
    """测试5值格式（Phase 1 MVP格式）"""
    bbox_list = [
        [10, 20, 110, 120, 0],
        [30, 40, 130, 140, 1],
        [50, 60, 150, 160, 2]
    ]
    
    prompts = bbox_process(bbox_list)
    
    assert len(prompts) == 3
    assert 0 in prompts
    assert 1 in prompts
    assert 2 in prompts
    assert prompts[0] == ((10, 20, 110, 120), "obj_0")
    assert prompts[1] == ((30, 40, 130, 140), "obj_1")
    assert prompts[2] == ((50, 60, 150, 160), "obj_2")
    print("✓ 5值格式测试通过")


def test_bbox_process_with_custom_labels():
    """测试自定义标签"""
    bbox_list = [
        [10, 20, 110, 120, 5],
        [30, 40, 130, 140, 8]
    ]
    labels = ["dog", "cat"]
    
    prompts = bbox_process(bbox_list, labels)
    
    assert prompts[5] == ((10, 20, 110, 120), "dog")
    assert prompts[8] == ((30, 40, 130, 140), "cat")
    print("✓ 自定义标签测试通过")


def test_bbox_process_invalid_format():
    """测试无效格式"""
    bbox_list = [
        [10, 20, 110]  # 只有3个值
    ]
    
    try:
        bbox_process(bbox_list)
        assert False, "应该抛出异常"
    except ValueError as e:
        assert "Invalid bbox format" in str(e)
        print("✓ 无效格式检测测试通过")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("bbox_process 函数测试")
    print("="*60 + "\n")
    
    try:
        test_bbox_process_4_values()
        test_bbox_process_5_values()
        test_bbox_process_with_custom_labels()
        test_bbox_process_invalid_format()
        
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

