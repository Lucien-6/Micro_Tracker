"""
Phase 2: 多帧处理核心功能测试

测试analyze_frame_segments函数的各种场景
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.process_video_multiframe import analyze_frame_segments


def test_analyze_frame_segments_basic():
    """测试基础帧段分析"""
    annotated = [0, 50, 120]
    total = 200
    segments = analyze_frame_segments(annotated, total)
    
    assert len(segments) == 3, f"期望3个段，实际{len(segments)}"
    assert segments[0] == (0, 49), f"段1错误: {segments[0]}"
    assert segments[1] == (50, 119), f"段2错误: {segments[1]}"
    assert segments[2] == (120, 199), f"段3错误: {segments[2]}"
    print("✓ 基础帧段分析测试通过")


def test_analyze_frame_segments_single():
    """测试单标注帧"""
    annotated = [0]
    total = 100
    segments = analyze_frame_segments(annotated, total)
    
    assert len(segments) == 1, f"期望1个段，实际{len(segments)}"
    assert segments[0] == (0, 99), f"段错误: {segments[0]}"
    print("✓ 单标注帧测试通过")


def test_analyze_frame_segments_dense():
    """测试密集标注（每10帧）"""
    annotated = [0, 10, 20, 30, 40]
    total = 50
    segments = analyze_frame_segments(annotated, total)
    
    assert len(segments) == 5, f"期望5个段，实际{len(segments)}"
    assert segments[0] == (0, 9), f"段1错误: {segments[0]}"
    assert segments[1] == (10, 19), f"段2错误: {segments[1]}"
    assert segments[2] == (20, 29), f"段3错误: {segments[2]}"
    assert segments[3] == (30, 39), f"段4错误: {segments[3]}"
    assert segments[4] == (40, 49), f"段5错误: {segments[4]}"
    print("✓ 密集标注测试通过")


def test_analyze_frame_segments_end():
    """测试标注在视频末尾"""
    annotated = [0, 90]
    total = 100
    segments = analyze_frame_segments(annotated, total)
    
    assert len(segments) == 2, f"期望2个段，实际{len(segments)}"
    assert segments[0] == (0, 89), f"段1错误: {segments[0]}"
    assert segments[1] == (90, 99), f"段2错误: {segments[1]}"
    print("✓ 末尾标注测试通过")


def test_analyze_frame_segments_empty():
    """测试空标注列表"""
    annotated = []
    total = 100
    segments = analyze_frame_segments(annotated, total)
    
    assert len(segments) == 0, f"期望0个段，实际{len(segments)}"
    print("✓ 空标注测试通过")


def test_analyze_frame_segments_adjacent():
    """测试相邻标注帧"""
    annotated = [0, 1, 2]
    total = 10
    segments = analyze_frame_segments(annotated, total)
    
    assert len(segments) == 3, f"期望3个段，实际{len(segments)}"
    assert segments[0] == (0, 0), f"段1错误: {segments[0]}"
    assert segments[1] == (1, 1), f"段2错误: {segments[1]}"
    assert segments[2] == (2, 9), f"段3错误: {segments[2]}"
    print("✓ 相邻标注帧测试通过")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Phase 2: 多帧处理核心功能测试")
    print("="*60 + "\n")
    
    try:
        test_analyze_frame_segments_basic()
        test_analyze_frame_segments_single()
        test_analyze_frame_segments_dense()
        test_analyze_frame_segments_end()
        test_analyze_frame_segments_empty()
        test_analyze_frame_segments_adjacent()
        
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

