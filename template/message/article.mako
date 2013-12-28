<%inherit file="base.mako" />

<%block name="content">
    <ArticleCount>${msg.article_count}</ArticleCount>
    <Articles>
    % for i in range(msg.article_count):
    <item>
        <Title><![CDATA[${msg.article[i]['title']}]]></Title>
        <Description><![CDATA[${msg.article[i]['desc']}]]></Description>
        <PicUrl><![CDATA[${msg.article[i]['pic_url']}]]></PicUrl>
        <Url><![CDATA[${msg.article[i]['url']}]]></Url>
    </item>
    % endfor
    </Articles>
</%block>
