import re
from astrbot.api import AstrBotConfig
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.message_components import Plain
from astrbot.api.star import Context, Star, register

@register("astrbot_plugin_thinktags", "长安某", "过滤标签和文本", "1.4.1")
class FilterthinktagsPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        result = event.get_result()
        chain = result.chain

        tags_to_filter = self.config.get('filtered_tags', [])
        prefixes_to_filter = self.config.get('filtered_prefixes', [])
        separator = self.config.get('content_separator', '')

        new_chain = []
        for component in chain:
            if isinstance(component, Plain):
                new_text = component.text
                
                # 只有当配置了分隔符时才进行分隔符过滤
                if separator:
                    if separator in new_text:
                        # 找到最后一个分隔符的位置
                        last_separator_index = new_text.rfind(separator)
                        # 保留最后一个分隔符之后的内容
                        new_text = new_text[last_separator_index + len(separator):]
                    else:
                        # 如果没有找到分隔符，清空文本
                        new_text = ""

                # 根据标签列表动态过滤标签
                if tags_to_filter and new_text:
                    tag_group = '|'.join(re.escape(tag) for tag in tags_to_filter)
                    pattern = rf'<({tag_group})>.*?</\1>\s*'
                    new_text = re.sub(pattern, '', new_text, flags=re.DOTALL)

                # 过滤无标签的、可能跨行的文本块
                if prefixes_to_filter and new_text:
                    for prefix in prefixes_to_filter:
                        pattern = rf'^{re.escape(prefix)}.*?(\n\n|\Z)'
                        new_text = re.sub(pattern, '', new_text, flags=re.DOTALL | re.MULTILINE)
                
                # 清理文本两端的空白字符
                stripped_text = new_text.strip()
                # 只有当处理后的文本不为空时，才将其添加回新的消息链
                if stripped_text:
                    new_chain.append(Plain(stripped_text))
            else:
                # 如果不是纯文本组件，则原样保留
                new_chain.append(component)

        # 用处理过的新消息链替换旧的消息链
        result.chain = new_chain
