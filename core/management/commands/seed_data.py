from django.core.management.base import BaseCommand

from core.models import (
    Article,
    Assessment,
    AssessmentOption,
    AssessmentQuestion,
    AssessmentResult,
    Category,
    Hotline,
    Institution,
    RelaxationMethod,
)


class Command(BaseCommand):
    help = "Seed sample categories and articles for demo."

    def handle(self, *args, **options):
        categories = [
            ("情绪管理", "识别情绪、缓解焦虑与提升心情的方法。"),
            ("睡眠与放松", "改善睡眠质量的知识与训练。"),
            ("社交与支持", "建立支持网络与减少孤独感。"),
            ("认知与记忆", "应对记忆力变化与注意力下降。"),
            ("身心共护", "身体疾病相关的心理疏导与照护建议。"),
        ]

        category_map = {}
        for name, description in categories:
            category, _ = Category.objects.get_or_create(
                name=name, defaults={"description": description}
            )
            category_map[name] = category

        filler_paragraphs = [
            "如果这些方法仍不足以缓解困扰，可以记录自己的感受与变化，"
            "这样在寻求专业帮助时能更准确地描述问题。",
            "请记得，持续的情绪困扰不是个人的失败，而是需要被照顾的信号。",
            "尝试在生活中保留固定的放松时间，比如晒太阳、散步或听舒缓音乐，"
            "这些小习惯会慢慢增强心理韧性。",
        ]

        def build_content(title, points):
            paragraphs = [
                f"{title} 在老年阶段较为常见，这并不代表你做得不好。"
                "很多人会在身体变化、家庭角色调整或生活节奏改变时出现类似感受，"
                "关键是先看见情绪，再逐步采取行动。",
                "情绪、睡眠与身体状态彼此影响。建议从规律作息、适度活动、"
                "减少过度刺激的信息摄入开始，让身心慢慢稳定下来。",
                "可以把大问题拆成小步骤，每天只关注一件能做到的小事，"
                "例如规律吃饭、与家人聊天或完成一次短途散步。",
                "建议要点：" + "；".join(points) + "。",
                "小练习：选择一个你能完成的小目标，用“我愿意尝试”开头写下计划，"
                "完成后给自己一个温和的肯定。",
                "如果困扰持续超过两周并影响睡眠或日常活动，建议及时联系"
                "专业人员或可信任的家人寻求支持。",
            ]
            content = "\n\n".join(paragraphs)
            idx = 0
            while len(content) < 650:
                content += "\n\n" + filler_paragraphs[idx % len(filler_paragraphs)]
                idx += 1
            return content

        samples = [
            {
                "title": "情绪低落时的自我关照方法",
                "summary": "通过识别情绪、稳定作息与小目标行动缓解低落。",
                "category": "情绪管理",
                "points": ["给情绪命名而不是压抑", "每天安排一件小确幸", "与可信任的人交流", "保持规律作息"],
            },
            {
                "title": "面对焦虑：从呼吸到行动的步骤",
                "summary": "用呼吸练习与行动清单帮助焦虑缓和。",
                "category": "情绪管理",
                "points": ["深呼吸放慢心率", "把担忧写下来", "只做当下能做的一步", "减少刺激性信息"],
            },
            {
                "title": "识别抑郁信号与寻求帮助",
                "summary": "了解抑郁信号，学会向家人与专业人士求助。",
                "category": "情绪管理",
                "points": ["持续两周以上的情绪低落", "兴趣下降与疲惫", "睡眠或食欲明显变化", "主动寻求支持"],
            },
            {
                "title": "生气与冲突：平和表达的技巧",
                "summary": "学会表达需求，减少冲突带来的伤害。",
                "category": "情绪管理",
                "points": ["用“我感到...”表达", "先暂停再沟通", "明确需求而不是指责", "给彼此冷静时间"],
            },
            {
                "title": "情绪日记：记录与整理心情",
                "summary": "通过记录心情提升自我理解与掌控感。",
                "category": "情绪管理",
                "points": ["每天记录三件小事", "写下感受与原因", "观察情绪变化", "给自己温和反馈"],
            },
            {
                "title": "改善失眠的晚间流程",
                "summary": "建立放松的睡前流程，帮助更快入睡。",
                "category": "睡眠与放松",
                "points": ["睡前1小时远离刺激", "固定上床时间", "避免过晚饮水", "温水泡脚放松"],
            },
            {
                "title": "午睡与作息的平衡",
                "summary": "合适的午睡时长帮助恢复精神，不影响夜间睡眠。",
                "category": "睡眠与放松",
                "points": ["午睡控制在30分钟内", "午后2点前结束", "避免长时间赖床", "保持固定作息"],
            },
            {
                "title": "身体放松训练：从脚到头",
                "summary": "渐进式放松训练帮助身体松弛。",
                "category": "睡眠与放松",
                "points": ["脚趾放松到小腿", "腹部深呼吸", "肩颈缓慢转动", "面部轻柔拉伸"],
            },
            {
                "title": "睡眠环境与光线噪音管理",
                "summary": "优化卧室环境，提升睡眠质量。",
                "category": "睡眠与放松",
                "points": ["保持柔和灯光", "减少噪音干扰", "控制室温湿度", "床铺舒适清洁"],
            },
            {
                "title": "生活习惯对睡眠的影响",
                "summary": "饮食、运动与日常习惯都会影响睡眠。",
                "category": "睡眠与放松",
                "points": ["白天适度运动", "晚餐清淡", "减少咖啡浓茶", "睡前远离手机"],
            },
            {
                "title": "和家人沟通的温和方式",
                "summary": "用温和表达提升沟通效果与亲密感。",
                "category": "社交与支持",
                "points": ["先表达感谢", "描述感受而非指责", "选择合适时间沟通", "耐心倾听对方"],
            },
            {
                "title": "参与社区活动的第一步",
                "summary": "通过小规模参与逐步融入社区。",
                "category": "社交与支持",
                "points": ["先参与兴趣小组", "从短时活动开始", "找一位熟人同行", "记录参与后的感受"],
            },
            {
                "title": "面对孤独感的日常练习",
                "summary": "用日常小行动缓解孤独感。",
                "category": "社交与支持",
                "points": ["固定时间与人联系", "培养兴趣爱好", "适度参与社区", "肯定自己的价值"],
            },
            {
                "title": "建立稳定支持网络",
                "summary": "打造稳定的人际支持体系，提升安全感。",
                "category": "社交与支持",
                "points": ["列出可信任的人", "定期联系", "主动表达需求", "遇到困难及时求助"],
            },
            {
                "title": "与老友重新联系的建议",
                "summary": "重新建立联系，延续友谊与支持。",
                "category": "社交与支持",
                "points": ["选择轻松话题开场", "分享近况与问候", "逐步恢复联系频率", "保持边界与尊重"],
            },
            {
                "title": "记忆力下降时的应对策略",
                "summary": "通过习惯与工具帮助记忆。",
                "category": "认知与记忆",
                "points": ["使用记事本与提醒", "固定放置重要物品", "分段记忆", "规律作息护脑"],
            },
            {
                "title": "注意力训练的小方法",
                "summary": "简单训练提升专注与反应。",
                "category": "认知与记忆",
                "points": ["一次只做一件事", "减少干扰", "短时专注练习", "适当休息恢复注意力"],
            },
            {
                "title": "认知衰退的早期迹象",
                "summary": "识别早期迹象，及时评估与干预。",
                "category": "认知与记忆",
                "points": ["记忆力明显下降", "理解困难增加", "日常安排混乱", "情绪变化较大"],
            },
            {
                "title": "日常生活的认知锻炼",
                "summary": "日常小练习帮助保持脑力。",
                "category": "认知与记忆",
                "points": ["阅读与复述", "学习新技能", "简单益智游戏", "与人交流思考"],
            },
            {
                "title": "保护大脑健康的生活建议",
                "summary": "从饮食、运动与作息保护脑健康。",
                "category": "认知与记忆",
                "points": ["均衡饮食", "坚持运动", "控制慢性病", "保持社交活跃"],
            },
            {
                "title": "慢病与情绪：长期治疗中的心理照护",
                "summary": "长期治疗中保持情绪稳定的策略。",
                "category": "身心共护",
                "points": ["允许情绪波动", "与医生沟通感受", "建立支持网络", "保持适度活动"],
            },
            {
                "title": "慢性疼痛与心情：日常缓解办法",
                "summary": "缓解疼痛带来的焦虑与无助感。",
                "category": "身心共护",
                "points": ["记录疼痛变化", "安排放松时段", "适度伸展", "与家人沟通需求"],
            },
            {
                "title": "康复期情绪起伏的应对方法",
                "summary": "恢复期保持耐心，稳住情绪。",
                "category": "身心共护",
                "points": ["关注小进步", "设定可完成的目标", "规律作息", "主动求助"],
            },
            {
                "title": "就医前的心理准备清单",
                "summary": "用清单降低就医焦虑与紧张。",
                "category": "身心共护",
                "points": ["写下问题清单", "准备既往记录", "规划陪同人员", "就诊后及时复盘"],
            },
            {
                "title": "家庭沟通中的理解与支持",
                "summary": "在家庭中建立理解与支持的沟通方式。",
                "category": "社交与支持",
                "points": ["表达真实感受", "倾听彼此需求", "减少指责语言", "共同制定计划"],
            },
            {
                "title": "白天活动与夜间睡眠的关系",
                "summary": "通过白天活动改善夜间睡眠。",
                "category": "睡眠与放松",
                "points": ["增加日间光照", "适度运动", "减少午睡过长", "晚间放松仪式"],
            },
            {
                "title": "放松练习：呼吸与肌肉放松",
                "summary": "通过呼吸与肌肉放松提升安稳感。",
                "category": "睡眠与放松",
                "points": ["腹式呼吸", "肩颈放松", "渐进式紧张与放松", "睡前10分钟练习"],
            },
            {
                "title": "记忆变化时的家庭协作",
                "summary": "通过家庭协作减轻记忆压力。",
                "category": "认知与记忆",
                "points": ["建立提醒清单", "固定物品位置", "家庭成员轮流陪伴", "减少催促"],
            },
        ]

        created_count = 0
        updated_count = 0
        for item in samples:
            category = category_map.get(item["category"])
            if not category:
                continue
            content = build_content(item["title"], item["points"])
            article, created = Article.objects.update_or_create(
                title=item["title"],
                defaults={
                    "summary": item["summary"],
                    "content": content,
                    "category": category,
                    "is_published": True,
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed completed: {len(category_map)} categories, "
                f"{created_count} created, {updated_count} updated."
            )
        )

        assessments_data = [
            {
                "name": "PHQ-9 抑郁自评",
                "category": "抑郁",
                "description": "评估过去两周抑郁相关感受的常见量表。",
                "instructions": "请回想过去两周内的感受，并选择最符合的选项。",
                "options": [
                    ("从不", 0),
                    ("有几天", 1),
                    ("超过一半天数", 2),
                    ("几乎每天", 3),
                ],
                "questions": [
                    "做事兴趣或乐趣缺乏",
                    "情绪低落、沮丧或无望",
                    "入睡困难、睡眠不稳或睡得过多",
                    "感觉疲劳或精力不足",
                    "食欲不振或吃得过多",
                    "觉得自己很糟或对自己失望",
                    "注意力不集中（阅读、看电视等）",
                    "行动或说话速度变慢，或相反变得坐立不安",
                    "出现伤害自己的想法",
                ],
                "results": [
                    (0, 4, "轻微或无抑郁", "当前抑郁症状较轻。", "保持规律作息与支持性社交。"),
                    (5, 9, "轻度抑郁", "可能存在轻度抑郁表现。", "可尝试放松训练与情绪记录。"),
                    (10, 14, "中度抑郁", "需要更多关注与支持。", "建议向专业人员咨询。"),
                    (15, 19, "中重度抑郁", "症状较明显，建议及时寻求帮助。", "优先联系专业机构。"),
                    (20, 27, "重度抑郁", "症状较重，请尽快寻求专业支持。", "必要时联系紧急援助。"),
                ],
            },
            {
                "name": "GAD-7 焦虑自评",
                "category": "焦虑",
                "description": "评估过去两周焦虑感受的常见量表。",
                "instructions": "请回想过去两周内的感受，并选择最符合的选项。",
                "options": [
                    ("从不", 0),
                    ("有几天", 1),
                    ("超过一半天数", 2),
                    ("几乎每天", 3),
                ],
                "questions": [
                    "感到紧张、焦虑或坐立不安",
                    "无法控制担忧",
                    "对许多事情过度担心",
                    "难以放松",
                    "因为不安而难以静坐",
                    "容易烦躁或易怒",
                    "担心会发生可怕的事情",
                ],
                "results": [
                    (0, 4, "轻微或无焦虑", "焦虑症状较轻。", "保持规律活动与放松训练。"),
                    (5, 9, "轻度焦虑", "可能存在轻度焦虑。", "建议进行呼吸放松与规律作息。"),
                    (10, 14, "中度焦虑", "焦虑程度较明显。", "建议寻求进一步支持。"),
                    (15, 21, "重度焦虑", "焦虑程度较重。", "请及时联系专业人员或热线。"),
                ],
            },
            {
                "name": "ISI 失眠严重度自评",
                "category": "睡眠",
                "description": "评估睡眠困难程度的常见量表。",
                "instructions": "请回想过去两周的睡眠情况，并选择最符合的选项。",
                "options": [
                    ("没有", 0),
                    ("轻微", 1),
                    ("中等", 2),
                    ("严重", 3),
                    ("非常严重", 4),
                ],
                "questions": [
                    "入睡困难的程度",
                    "维持睡眠的困难程度",
                    "早醒后的再次入睡困难程度",
                    "对当前睡眠满意度",
                    "睡眠问题对日间功能的影响程度",
                    "他人注意到你的睡眠问题程度",
                    "睡眠问题带来的担忧或困扰程度",
                ],
                "results": [
                    (0, 7, "无明显失眠", "当前失眠症状较轻。", "保持良好作息与睡前放松。"),
                    (8, 14, "轻度失眠", "可能存在轻度睡眠问题。", "可尝试放松训练与睡前仪式。"),
                    (15, 21, "中度失眠", "睡眠问题较明显。", "建议进一步咨询专业人员。"),
                    (22, 28, "重度失眠", "睡眠问题严重。", "请尽快寻求专业帮助。"),
                ],
            },
        ]

        for item in assessments_data:
            assessment, _ = Assessment.objects.update_or_create(
                name=item["name"],
                defaults={
                    "category": item["category"],
                    "description": item["description"],
                    "instructions": item["instructions"],
                    "is_published": True,
                },
            )

            for index, question_text in enumerate(item["questions"], start=1):
                question, _ = AssessmentQuestion.objects.update_or_create(
                    assessment=assessment,
                    order=index,
                    defaults={"text": question_text},
                )
                for opt_index, (opt_text, opt_score) in enumerate(item["options"], start=1):
                    AssessmentOption.objects.update_or_create(
                        question=question,
                        order=opt_index,
                        defaults={"text": opt_text, "score": opt_score},
                    )

            for min_score, max_score, title, summary, advice in item["results"]:
                AssessmentResult.objects.update_or_create(
                    assessment=assessment,
                    min_score=min_score,
                    defaults={
                        "max_score": max_score,
                        "title": title,
                        "summary": summary,
                        "advice": advice,
                    },
                )

        relaxation_methods = [
            {
                "name": "腹式呼吸",
                "description": "通过缓慢深呼吸稳定情绪。",
                "steps": "坐稳或平躺，吸气时腹部鼓起，呼气时腹部收回，重复 3-5 分钟。",
                "suggested_minutes": 5,
            },
            {
                "name": "渐进性肌肉放松",
                "description": "从脚到头部逐步紧张再放松。",
                "steps": "依次绷紧脚、腿、腹、肩等部位 3 秒，再放松。",
                "suggested_minutes": 10,
            },
            {
                "name": "正念三分钟",
                "description": "把注意力放在当下呼吸与身体感受。",
                "steps": "闭眼三分钟，觉察呼吸起伏与身体接触点。",
                "suggested_minutes": 3,
            },
            {
                "name": "舒缓伸展",
                "description": "轻柔拉伸肩颈与背部。",
                "steps": "缓慢转动肩颈、伸展背部，每个动作保持 10 秒。",
                "suggested_minutes": 8,
            },
            {
                "name": "音乐放松",
                "description": "聆听轻音乐帮助身心放松。",
                "steps": "选择舒缓音乐，专注聆听 10 分钟。",
                "suggested_minutes": 10,
            },
        ]

        for method in relaxation_methods:
            RelaxationMethod.objects.update_or_create(
                name=method["name"],
                defaults={
                    "description": method["description"],
                    "steps": method["steps"],
                    "suggested_minutes": method["suggested_minutes"],
                    "is_active": True,
                },
            )

        institutions = [
            {
                "name": "南京脑科医院",
                "region_type": Institution.REGION_LOCAL,
                "province": "江苏省",
                "city": "南京市",
                "address": "江苏省南京市广州路264号",
                "phone": "025-83723287",
                "service_hours": "以医院公告为准",
                "description": "精神心理专科医院（来源：公开资料）。",
            },
            {
                "name": "苏州市广济医院",
                "region_type": Institution.REGION_PROVINCE,
                "province": "江苏省",
                "city": "苏州市",
                "address": "江苏省苏州市广济路286号",
                "phone": "0512-65331367",
                "service_hours": "以医院公告为准",
                "description": "精神卫生专科医院（来源：公开资料）。",
            },
            {
                "name": "无锡市精神卫生中心",
                "region_type": Institution.REGION_PROVINCE,
                "province": "江苏省",
                "city": "无锡市",
                "address": "江苏省无锡市钱荣路156号",
                "phone": "0510-83012698",
                "service_hours": "以医院公告为准",
                "description": "提供心理咨询与精神卫生服务（来源：公开资料）。",
            },
            {
                "name": "常州市德安医院",
                "region_type": Institution.REGION_PROVINCE,
                "province": "江苏省",
                "city": "常州市",
                "address": "江苏省常州市桃园路1号",
                "phone": "0519-88042888",
                "service_hours": "以医院公告为准",
                "description": "精神卫生与心理健康服务机构（来源：公开资料）。",
            },
            {
                "name": "南通市第四人民医院",
                "region_type": Institution.REGION_PROVINCE,
                "province": "江苏省",
                "city": "南通市",
                "address": "江苏省南通市城港路37号",
                "phone": "0513-85606903",
                "service_hours": "以医院公告为准",
                "description": "精神卫生与心理健康服务机构（来源：公开资料）。",
            },
            {
                "name": "盐城市第四人民医院",
                "region_type": Institution.REGION_PROVINCE,
                "province": "江苏省",
                "city": "盐城市",
                "address": "江苏省盐城市开放大道124号",
                "phone": "0515-88550242",
                "service_hours": "以医院公告为准",
                "description": "精神卫生与心理健康服务机构（来源：公开资料）。",
            },
            {
                "name": "连云港市第四人民医院",
                "region_type": Institution.REGION_PROVINCE,
                "province": "江苏省",
                "city": "连云港市",
                "address": "江苏省连云港市海州区西门路81号",
                "phone": "0518-85708999",
                "service_hours": "以医院公告为准",
                "description": "精神卫生与心理健康服务机构（来源：公开资料）。",
            },
            {
                "name": "淮安市第三人民医院",
                "region_type": Institution.REGION_PROVINCE,
                "province": "江苏省",
                "city": "淮安市",
                "address": "江苏省淮安市淮海西路272号",
                "phone": "0517-3664728",
                "service_hours": "以医院公告为准",
                "description": "精神卫生与心理健康服务机构（来源：公开资料）。",
            },
            {
                "name": "泰州市第四人民医院",
                "region_type": Institution.REGION_PROVINCE,
                "province": "江苏省",
                "city": "泰州市",
                "address": "江苏省泰州市稻河路58号",
                "phone": "0523-86611007",
                "service_hours": "以医院公告为准",
                "description": "精神卫生与心理健康服务机构（来源：公开资料）。",
            },
            {
                "name": "徐州市东方人民医院",
                "region_type": Institution.REGION_PROVINCE,
                "province": "江苏省",
                "city": "徐州市",
                "address": "江苏省徐州市云龙区东甸子铜山路379号",
                "phone": "0516-83447100",
                "service_hours": "以医院公告为准",
                "description": "精神卫生与心理健康服务机构（来源：公开资料）。",
            },
            {
                "name": "北京心理危机研究与干预中心",
                "region_type": Institution.REGION_NATIONAL,
                "province": "北京市",
                "city": "北京市",
                "address": "北京市昌平区回龙观（北京回龙观医院）",
                "phone": "800-810-1117 / 010-8295-1332",
                "service_hours": "7×24 小时",
                "description": "全国心理援助热线管理项目（来源：公开资料）。",
            },
        ]

        for item in institutions:
            Institution.objects.update_or_create(
                name=item["name"],
                region_type=item["region_type"],
                defaults=item,
            )

        hotlines = [
            {
                "name": "全国统一心理援助热线",
                "region_type": Hotline.REGION_NATIONAL,
                "phone": "12356",
                "is_24h": False,
                "is_emergency": False,
                "description": "全国统一心理援助热线（每日不少于18小时服务）。",
            },
            {
                "name": "北京心理援助热线（24小时）",
                "region_type": Hotline.REGION_NATIONAL,
                "phone": "800-810-1117 / 010-8295-1332",
                "is_24h": True,
                "is_emergency": False,
                "description": "由北京心理危机研究与干预中心提供服务。",
            },
            {
                "name": "江苏省心理援助热线",
                "region_type": Hotline.REGION_PROVINCE,
                "province": "江苏省",
                "phone": "12356 / 025-83712977",
                "is_24h": False,
                "is_emergency": False,
                "description": "江苏省心理援助热线（原心理危机干预热线）。",
            },
            {
                "name": "南京市心理援助热线",
                "region_type": Hotline.REGION_LOCAL,
                "province": "江苏省",
                "city": "南京市",
                "phone": "12356 / 025-83712977",
                "is_24h": False,
                "is_emergency": False,
                "description": "南京市心理援助热线。",
            },
            {
                "name": "紧急医疗救援 120",
                "region_type": Hotline.REGION_NATIONAL,
                "phone": "120",
                "is_24h": True,
                "is_emergency": True,
                "description": "出现紧急情况请优先拨打 120。",
            },
            {
                "name": "紧急报警 110",
                "region_type": Hotline.REGION_NATIONAL,
                "phone": "110",
                "is_24h": True,
                "is_emergency": True,
                "description": "紧急情况下可拨打报警电话。",
            },
        ]

        for item in hotlines:
            Hotline.objects.update_or_create(
                name=item["name"],
                region_type=item["region_type"],
                phone=item["phone"],
                defaults=item,
            )
