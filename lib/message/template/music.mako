<%inherit file="base.mako" />

<%block name="content">
    <Music>
        <Title><![CDATA[${msg.content.music_title}]]></Title>
        <Description><![CDATA[${msg.content.music_desc}]]></Description>
        <MusicUrl><![CDATA[${msg.content.music_url]]></MusicUrl>
        <HQMusicUrl><![CDATA[${msg.content.music_url_hq]]></HQMusicUrl>
        <ThumbMediaId><![CDATA[${msg.content.media_id}]]></ThumbMediaId>
    </Music>
</%block>
