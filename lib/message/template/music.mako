<%inherit file="base.mako" />

<%block name="content">
    <Music>
        <Title><![CDATA[${msg.content.title}]]></Title>
        <Description><![CDATA[${msg.content.desc}]]></Description>
        <MusicUrl><![CDATA[${msg.content.url}]]></MusicUrl>
        <HQMusicUrl><![CDATA[${msg.content.url_hq}]]></HQMusicUrl>
        <ThumbMediaId><![CDATA[${msg.content.media_id}]]></ThumbMediaId>
    </Music>
</%block>
