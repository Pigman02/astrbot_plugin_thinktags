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
        separator = self.config.get('content_separator', '@@@')

        new_chain = []
        for component in chain:
            if isinstance(component, Plain):
                new_text = component.text
                
                # 使用分隔符过滤思考内容
                if separator and separator in new_text:
                    last_separator_index = new_text.rfind(separator)
                    new_text = new_text[last_separator_index + len(separator):]

                # 原有的标签过滤
                if tags_to_filter:
                    tag_group = '|'.join(re.escape(tag) for tag in tags_to_filter)
                    pattern = rf'<({tag_group})>.*?</\1>\s*'
                    new_text = re.sub(pattern, '', new_text, flags=re.DOTALL)

                # 原有的前缀过滤
                if prefixes_to_filter:
                    for prefix in prefixes_to_filter:
                        pattern = rf'^{re.escape(prefix)}.*?(\n\n|\Z)'
                        new_text = re.sub(pattern, '', new_text, flags=re.DOTALL | re.MULTILINE)
                
                stripped_text = new_text.strip()
                if stripped_text:
                    new_chain.append(Plain(stripped_text))
            else:
                new_chain.append(component)

        result.chain = new_chain
