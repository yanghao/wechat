<%inherit file="base.mako" />

<%block name="content">
    <ArticleCount>${msg.content.news_count}</ArticleCount>
    <Articles>
    % for i in range(msg.content.news_count):
    <item>
        <Title><![CDATA[${msg.content.news[i]['title']}]]></Title>
        <Description><![CDATA[${msg.content.news[i]['desc']}]]></Description>
        <PicUrl><![CDATA[${msg.content.news[i]['pic_url']}]]></PicUrl>
        <Url><![CDATA[${msg.content.news[i]['url']}]]></Url>
    </item>
    % endfor
    </Articles>
</%block>
