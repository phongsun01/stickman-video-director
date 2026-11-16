#!/usr/bin/env python3
"""Story Flow Scaffolding Engine for Stickman Video Director.

Generates production-ready storyboard templates based on 6 proven Narrative Story Flows:
1. pas: Problem - Agitate - Solution
2. three-reasons: Three Reasons Why
3. myth-buster: Myth Buster
4. before-after: Before - After - Bridge
5. hero-journey: Hero's Journey Mini
6. curiosity-gap: Curiosity Gap / Mystery

Usage:
    python3 scripts/story-flow-scaffold.py --flow pas --topic "Quản lý thời gian" --duration 40 --output story.json
    python3 scripts/story-flow-scaffold.py --flow myth-buster --topic "Uống 2 lít nước" --format markdown
"""
import argparse
import json
import sys
from pathlib import Path

FLOW_DEFINITIONS = {
    "pas": {
        "name": "Problem - Agitate - Solution (PAS)",
        "description": "Nêu vấn đề nhức nhối, khuấy động nỗi đau, đưa ra giải pháp cứu cánh và kêu gọi hành động.",
        "shots": [
            {
                "role": "hook_problem",
                "purpose": "Đặt vấn đề trực diện, chạm trúng nỗi đau khán giả",
                "time_ratio": 0.12,
                "action": "Người que ôm đầu bất lực trước màn hình/tài liệu ngổn ngang, biểu cảm bối rối",
                "camera": "Zoom-in nhanh vào mặt nhân vật",
                "sfx": "alarm_bell",
                "default_vo_vi": "Bạn có đang bế tắc vì {topic} mỗi ngày mà không biết bắt đầu từ đâu?",
                "default_vo_en": "Are you struggling with {topic} every single day without knowing where to start?"
            },
            {
                "role": "agitate",
                "purpose": "Khuấy động nỗi đau, chỉ ra hậu quả nếu không thay đổi",
                "time_ratio": 0.28,
                "action": "Thanh năng lượng tụt về 0%, bóng ma áp lực đè bẹp người que, đồng hồ quay vùn vụt",
                "camera": "Pan ngang sang cảnh lịch trình kín đặc màu đỏ",
                "sfx": "whoosh_fall",
                "default_vo_vi": "Càng chần chừ, bạn càng lãng phí thời gian và năng lượng quý giá.",
                "default_vo_en": "The longer you wait, the more precious time and energy you lose."
            },
            {
                "role": "solution",
                "purpose": "Hé lộ giải pháp đột phá, cơ chế thực hiện rõ ràng",
                "time_ratio": 0.40,
                "action": "Bóng đèn sáng bừng trên đầu người que, mở ra phương pháp mới, đồ thị bật tăng",
                "camera": "Zoom-out rộng mở ra không gian tươi sáng",
                "sfx": "chime_success",
                "default_vo_vi": "Chỉ cần áp dụng giải pháp này: đơn giản hóa từng bước và thực hiện liên tục.",
                "default_vo_en": "Here is the exact solution: break it down into simple steps and stay consistent."
            },
            {
                "role": "cta",
                "purpose": "Kêu gọi hành động hoặc bài học chốt hạ",
                "time_ratio": 0.20,
                "action": "Người que thảnh thơi mỉm cười, chỉ tay vào nút Đăng ký / Lưu video",
                "camera": "Cố định trung cảnh ấm áp",
                "sfx": "click_clean",
                "default_vo_vi": "Hãy thử áp dụng ngay hôm nay và bấm lưu lại video này nhé!",
                "default_vo_en": "Try this today and make sure to save this video for later!"
            }
        ]
    },
    "three-reasons": {
        "name": "Three Reasons Why (Quy tắc Tam phân)",
        "description": "Liệt kê 3 luận điểm thuyết phục, phân tích logic, kết luận súc tích.",
        "shots": [
            {
                "role": "hook",
                "purpose": "Câu hỏi tò mò kích thích người xem",
                "time_ratio": 0.12,
                "action": "Người que giơ 3 ngón tay, số 3 xuất hiện nổi bật",
                "camera": "Zoom-in",
                "sfx": "pop_badge",
                "default_vo_vi": "Đây là 3 lý do vì sao {topic} quan trọng hơn bạn nghĩ rất nhiều.",
                "default_vo_en": "Here are 3 reasons why {topic} matters much more than you think."
            },
            {
                "role": "reason_1",
                "purpose": "Lý do thứ nhất: Nguyên nhân phổ biến nhất",
                "time_ratio": 0.28,
                "action": "Người que chỉ vào biểu đồ / mô hình minh họa luận điểm 1",
                "camera": "Pan trái",
                "sfx": "whoosh_clean",
                "default_vo_vi": "Thứ nhất: Giúp bạn tiết kiệm đến 50% công sức mà vẫn đạt hiệu quả tối đa.",
                "default_vo_en": "First: It saves you up to 50% of effort while maximizing results."
            },
            {
                "role": "reason_2",
                "purpose": "Lý do thứ hai: Yếu tố ít ai ngờ tới",
                "time_ratio": 0.28,
                "action": "Người que mở hộp bí mật, ánh sáng phát ra ngạc nhiên",
                "camera": "Góc quay cận cảnh",
                "sfx": "magical_sparkle",
                "default_vo_vi": "Thứ hai: Tạo ra thói quen vững chắc mà không hề tốn ý chí.",
                "default_vo_en": "Second: It builds lasting habits without draining your willpower."
            },
            {
                "role": "reason_3_conclusion",
                "purpose": "Lý do thứ ba + Lời khuyên hành động",
                "time_ratio": 0.32,
                "action": "Người que giơ ngón cái, biểu tượng hoàn thành tick xanh",
                "camera": "Zoom-out toàn cảnh",
                "sfx": "chime_bell",
                "default_vo_vi": "Và thứ ba: Mang lại sự tự do đích thực. Bấm theo dõi để xem thêm mẹo hay!",
                "default_vo_en": "And third: It gives you real freedom. Follow for more insights!"
            }
        ]
    },
    "myth-buster": {
        "name": "Myth Buster (Đập tan ngộ nhận)",
        "description": "Đặt ra ngộ nhận phổ biến, lật ngược sự thật bằng bằng chứng và đưa ra insight đúng đắn.",
        "shots": [
            {
                "role": "the_myth",
                "purpose": "Nêu ngộ nhận mà số đông đang tin sái cổ",
                "time_ratio": 0.15,
                "action": "Người que gật gù trước biển báo ghi niềm tin thông thường",
                "camera": "Trung cảnh",
                "sfx": "bubble_pop",
                "default_vo_vi": "Có thể bạn đang tin rằng {topic} luôn đúng trong mọi trường hợp.",
                "default_vo_en": "You probably believe that {topic} is always true."
            },
            {
                "role": "the_rejection",
                "purpose": "Bác bỏ gây sốc bằng thực tế",
                "time_ratio": 0.25,
                "action": "Dấu gạch chéo đỏ khổng lồ giáng xuống làm vỡ tan bảng tin",
                "camera": "Rung máy nhẹ (camera shake)",
                "sfx": "punch_impact",
                "default_vo_vi": "Nhưng sự thật hoàn toàn ngược lại!",
                "default_vo_en": "But the reality is completely the opposite!"
            },
            {
                "role": "the_proof",
                "purpose": "Bằng chứng khoa học / thực nghiệm",
                "time_ratio": 0.35,
                "action": "Người que đeo kính hiển vi, đối chiếu số liệu và kết quả thực",
                "camera": "Pan cận cảnh",
                "sfx": "data_counter",
                "default_vo_vi": "Các nghiên cứu thực tế cho thấy cơ chế vận hành hoàn toàn khác biệt.",
                "default_vo_en": "Real data shows that the mechanism operates very differently."
            },
            {
                "role": "the_insight",
                "purpose": "Góc nhìn đúng đắn và cách ứng dụng",
                "time_ratio": 0.25,
                "action": "Người que gật đầu tâm đắc, chỉ vào phương án tối ưu",
                "camera": "Toàn cảnh tươi sáng",
                "sfx": "chime_success",
                "default_vo_vi": "Hiểu đúng bản chất sẽ giúp bạn đi nhanh hơn gấp 10 lần. Lưu lại ngay nhé!",
                "default_vo_en": "Understanding the core truth will put you 10x ahead. Save this now!"
            }
        ]
    },
    "before-after": {
        "name": "Before - After - Bridge (BAB)",
        "description": "Khắc họa trạng thái trước đau khổ, trạng thái sau tuyệt vời và cây cầu kết nối.",
        "shots": [
            {
                "role": "before",
                "purpose": "Trạng thái trước chật vật, luẩn quẩn",
                "time_ratio": 0.20,
                "action": "Người que đi dưới trời mưa, cúi gằm mặt mệt mỏi",
                "camera": "Tone màu xám/trầm",
                "sfx": "rain_ambience",
                "default_vo_vi": "Trước đây khi nhắc đến {topic}, tôi luôn cảm thấy kiệt sức và bế tắc.",
                "default_vo_en": "Before this, whenever dealing with {topic}, I felt completely drained."
            },
            {
                "role": "after",
                "purpose": "Trạng thái sau lý tưởng, thành công rực rỡ",
                "time_ratio": 0.25,
                "action": "Người que đứng dưới ánh mặt trời rực rỡ, cười tươi rói",
                "camera": "Màu sắc bừng sáng, zoom-in",
                "sfx": "magical_sparkle",
                "default_vo_vi": "Nhưng bây giờ, mọi thứ trở nên nhẹ nhàng, tự tin và trơn tru.",
                "default_vo_en": "Now, everything runs smoothly, confidently, and effortlessly."
            },
            {
                "role": "the_bridge",
                "purpose": "Cây cầu bí mật kết nối hai trạng thái",
                "time_ratio": 0.35,
                "action": "Người que xây một cây cầu vượt qua vực thẳm",
                "camera": "Góc nhìn toàn cảnh hoành tráng",
                "sfx": "gear_turn",
                "default_vo_vi": "Bí quyết chính là thay đổi góc nhìn và áp dụng nguyên lý đơn giản này.",
                "default_vo_en": "The bridge that changed everything was shifting perspective with this rule."
            },
            {
                "role": "action",
                "purpose": "Bước đi đầu tiên người xem cần làm ngay",
                "time_ratio": 0.20,
                "action": "Người que bước qua cầu, vẫy gọi khán giả cùng đi",
                "camera": "Chuyển động tiến về phía trước",
                "sfx": "click_clean",
                "default_vo_vi": "Hãy bắt đầu bước đầu tiên ngay hôm nay!",
                "default_vo_en": "Take your very first step today!"
            }
        ]
    },
    "hero-journey": {
        "name": "Hero's Journey Mini (Hành trình Người que)",
        "description": "Khởi đầu ngây thơ -> Thất bại ê chề -> Gặp thầy giỏi/Bí kíp -> Chiến thắng vẻ vang.",
        "shots": [
            {
                "role": "ordinary_world",
                "purpose": "Stickman khởi đầu với ước mơ lớn",
                "time_ratio": 0.15,
                "action": "Người que Bob tung tăng bước vào hành trình mới đầy hào hứng",
                "camera": "Trung cảnh",
                "sfx": "whistle_cheerful",
                "default_vo_vi": "Bob rất hào hứng khi quyết định chinh phục {topic}.",
                "default_vo_en": "Bob was super excited to master {topic}."
            },
            {
                "role": "crisis",
                "purpose": "Gặp chướng ngại và nếm mùi thất bại hài hước",
                "time_ratio": 0.30,
                "action": "Chướng ngại vật rơi xuống đè bẹp Bob, mắt hoa lên sao xẹt",
                "camera": "Rung máy + Zoom-in cận",
                "sfx": "cartoon_bonk",
                "default_vo_vi": "Nhưng đời không như mơ, cậu ấy liên tục vấp ngã ê chề.",
                "default_vo_en": "But reality hit hard, and he fell flat on his face."
            },
            {
                "role": "the_mentor",
                "purpose": "Học được bí kíp chân truyền",
                "time_ratio": 0.30,
                "action": "Sư phụ người que râu bạc xuất hiện trao cho cuốn bí kíp tỏa sáng",
                "camera": "Pan theo luồng ánh sáng",
                "sfx": "divine_chime",
                "default_vo_vi": "May mắn thay, Bob nhận ra sai lầm cốt lõi và điều chỉnh lại phương pháp.",
                "default_vo_en": "Luckily, Bob identified the core mistake and adjusted his method."
            },
            {
                "role": "victory",
                "purpose": "Trận tái đấu và chiến thắng huy hoàng",
                "time_ratio": 0.25,
                "action": "Bob nâng bổng chướng ngại vật ném bay lên trời, đeo kính râm cool ngầu",
                "camera": "Hất từ dưới lên (low-angle hero shot)",
                "sfx": "victory_fanfare",
                "default_vo_vi": "Giờ đây Bob đã thành công vượt bậc. Bạn cũng làm được như Bob!",
                "default_vo_en": "Now Bob has won. You can do it just like Bob!"
            }
        ]
    },
    "curiosity-gap": {
        "name": "Curiosity Gap / Mystery (Bí ẩn hé lộ)",
        "description": "Đặt câu hỏi kỳ lạ -> Dẫn dắt qua các manh mối -> Bẻ lái bất ngờ và tiết lộ chân tướng.",
        "shots": [
            {
                "role": "the_hook_mystery",
                "purpose": "Câu hỏi hóc búa gây tò mò tột độ",
                "time_ratio": 0.15,
                "action": "Dấu hỏi chấm khổng lồ xoay tròn, người que ngơ ngác quan sát",
                "camera": "Slow zoom-in bí ẩn",
                "sfx": "mystery_drone",
                "default_vo_vi": "Bạn đã bao giờ thắc mắc điều gì thực sự xảy ra đằng sau {topic}?",
                "default_vo_en": "Have you ever wondered what actually happens behind {topic}?"
            },
            {
                "role": "clue_investigation",
                "purpose": "Điều tra manh mối và các giả thuyết sai lầm",
                "time_ratio": 0.35,
                "action": "Người que cầm kính lúp lần theo các dấu vết bí ẩn trên sàn",
                "camera": "Tracking lateral shot",
                "sfx": "footsteps_suspense",
                "default_vo_vi": "Nhiều người đoán mò nhưng các bằng chứng lại dẫn tới một hướng khác.",
                "default_vo_en": "People made guesses, but the evidence pointed somewhere unexpected."
            },
            {
                "role": "the_twist_reveal",
                "purpose": "Cú bẻ lái và tiết lộ chân tướng sự thật",
                "time_ratio": 0.30,
                "action": "Tấm màn nhung kéo sang một bên, để lộ bí mật chấn động",
                "camera": "Quick zoom-in vào chi tiết mấu chốt",
                "sfx": "dramatic_reveal",
                "default_vo_vi": "Và đây chính là sự thật mà rất ít người biết được!",
                "default_vo_en": "And here is the shocking truth that very few people know!"
            },
            {
                "role": "open_question",
                "purpose": "Đặt câu hỏi mở kích thích bình luận",
                "time_ratio": 0.20,
                "action": "Người que nhìn thẳng vào khán giả, nhướn mày tò mò",
                "camera": "Trung cảnh trực diện",
                "sfx": "subtle_ting",
                "default_vo_vi": "Bạn nghĩ sao về điều này? Hãy để lại bình luận bên dưới nhé!",
                "default_vo_en": "What do you think about this? Let me know in the comments below!"
            }
        ]
    }
}


def build_story_scaffold(flow_key: str, topic: str, duration: float = 40.0, lang: str = "vi") -> dict:
    if flow_key not in FLOW_DEFINITIONS:
        raise ValueError(f"Unknown flow: '{flow_key}'. Choose from: {list(FLOW_DEFINITIONS.keys())}")

    flow = FLOW_DEFINITIONS[flow_key]
    shots_def = flow["shots"]
    shots_out = []
    current_time = 0.0

    for i, s_def in enumerate(shots_def):
        shot_dur = round(duration * s_def["time_ratio"], 1)
        # Ensure last shot matches exact duration
        if i == len(shots_def) - 1:
            shot_dur = round(duration - current_time, 1)

        vo_template = s_def["default_vo_vi"] if lang == "vi" else s_def["default_vo_en"]
        vo_text = vo_template.format(topic=topic)

        shots_out.append({
            "shot_id": i + 1,
            "role": s_def["role"],
            "purpose": s_def["purpose"],
            "start": round(current_time, 1),
            "end": round(current_time + shot_dur, 1),
            "duration": shot_dur,
            "action": s_def["action"],
            "camera": s_def["camera"],
            "sfx_cue": s_def["sfx"],
            "narration": vo_text
        })
        current_time += shot_dur

    return {
        "title": f"{topic} ({flow['name']})",
        "flow": flow_key,
        "flow_name": flow["name"],
        "description": flow["description"],
        "total_duration": duration,
        "language": lang,
        "shots": shots_out
    }


def to_markdown(story: dict) -> str:
    md = [
        f"# Kịch Bản Hoạt Hình: {story['title']}",
        f"- **Cấu trúc dẫn chuyện:** {story['flow_name']}",
        f"- **Thời lượng:** {story['total_duration']}s | **Ngôn ngữ:** {story['language']}",
        f"- **Tóm tắt cấu trúc:** {story['description']}",
        "",
        "## Storyboard Chi Tiết",
        "| Shot | Thời gian | Vai trò | Lời thoại (VO) | Hành động người que & Camera | SFX Gợi ý |",
        "| :---: | :---: | :--- | :--- | :--- | :--- |"
    ]
    for s in story["shots"]:
        md.append(f"| {s['shot_id']} | {s['start']}s - {s['end']}s ({s['duration']}s) | **{s['role']}**<br>_{s['purpose']}_ | \"{s['narration']}\" | {s['action']}<br>*(Cam: {s['camera']})* | `{s['sfx_cue']}` |")
    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--flow", choices=list(FLOW_DEFINITIONS.keys()), default="pas",
                        help="Narrative flow to use (default: pas)")
    parser.add_argument("--topic", default="Chủ đề của bạn", help="Story topic / subject")
    parser.add_argument("--duration", type=float, default=40.0, help="Total video duration in seconds (default: 40)")
    parser.add_argument("--lang", choices=["vi", "en"], default="vi", help="Narration language (default: vi)")
    parser.add_argument("--format", choices=["json", "markdown"], default="json", help="Output format (default: json)")
    parser.add_argument("--output", help="Optional output file path")
    parser.add_argument("--list-flows", action="store_true", help="List all available flows and exit")
    args = parser.parse_args()

    if args.list_flows:
        print("DANH SÁCH 6 NARRATIVE STORY FLOWS:")
        for k, v in FLOW_DEFINITIONS.items():
            print(f"  - {k:15s} : {v['name']} ({len(v['shots'])} shots) - {v['description']}")
        return

    story = build_story_scaffold(args.flow, args.topic, args.duration, args.lang)

    if args.format == "markdown":
        output_content = to_markdown(story)
    else:
        output_content = json.dumps(story, ensure_ascii=False, indent=2)

    if args.output:
        out_p = Path(args.output).expanduser().resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(output_content, encoding="utf-8")
        print(f"Story scaffold written to: {out_p}")
    else:
        print(output_content)


if __name__ == "__main__":
    main()
