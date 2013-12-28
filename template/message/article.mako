<%inherit file="base.mako" />

<%block name="content">
    <ArticleCount>${msg.content.article_count}</ArticleCount>
    <Articles>
    % for i in range(msg.article_count):
    <item>
        <Title><![CDATA[${msg.content.article[i]['title']}]]></Title>
        <Description><![CDATA[${msg.content.article[i]['desc']}]]></Description>
        <PicUrl><![CDATA[${msg.content.article[i]['pic_url']}]]></PicUrl>
        <Url><![CDATA[${msg..content.article[i]['url']}]]></Url>
    </item>
    % endfor
    </Articles>
</%block>
