"""
Phase 2: 对象ID管理测试
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from micro_tracker.components.video_widgets import OverlayLayer


def test_object_registration():
    """测试对象注册"""
    overlay = OverlayLayer()
    
    overlay.register_object(0, 0)
    assert 0 in overlay.object_registry
    assert overlay.object_registry[0]["first_frame"] == 0
    assert overlay.object_registry[0]["frames"] == [0]
    
    # 在第50帧再次注册对象0
    overlay.register_object(0, 50)
    assert overlay.object_registry[0]["frames"] == [0, 50]
    
    print("✓ 对象注册测试通过")


def test_get_next_object_id():
    """测试获取下一个可用ID"""
    overlay = OverlayLayer()
    
    assert overlay.get_next_object_id() == 0
    
    overlay.register_object(0, 0)
    overlay.register_object(1, 0)
    
    assert overlay.get_next_object_id() == 2
    print("✓ 获取下一个ID测试通过")


def test_annotation_mode_new_object():
    """测试新对象模式"""
    overlay = OverlayLayer()
    overlay.set_annotation_mode("new_object")
    
    overlay.start_drawing(10, 10)
    assert overlay.current_bbox[4] == 0
    
    print("✓ 新对象模式测试通过")


def test_annotation_mode_refine_object():
    """测试修正对象模式"""
    overlay = OverlayLayer()
    
    overlay.register_object(0, 0)
    overlay.set_annotation_mode("refine_object", 0)
    
    overlay.start_drawing(10, 10)
    assert overlay.current_bbox[4] == 0
    
    print("✓ 修正对象模式测试通过")


def test_object_color_consistency():
    """测试对象颜色一致性"""
    overlay = OverlayLayer()
    
    overlay.register_object(0, 0)
    color1 = overlay.get_object_color(0)
    
    overlay.register_object(0, 50)
    color2 = overlay.get_object_color(0)
    
    assert color1 == color2, "同一对象在不同帧应使用相同颜色"
    print("✓ 对象颜色一致性测试通过")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Phase 2: 对象ID管理测试")
    print("="*60 + "\n")
    
    try:
        test_object_registration()
        test_get_next_object_id()
        test_annotation_mode_new_object()
        test_annotation_mode_refine_object()
        test_object_color_consistency()
        
        print("\n" + "="*60)
        print("✓✓✓ 所有测试通过！ ✓✓✓")
        print("="*60)
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

