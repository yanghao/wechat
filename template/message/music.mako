<%inherit file="base.mako" />

<%block name="content">
    <Music>
        <Title><![CDATA[${msg.music_title}]]></Title>
        <Description><![CDATA[${msg.music_desc}]]></Description>
        <MusicUrl><![CDATA[${msg.music_url]]></MusicUrl>
        <HQMusicUrl><![CDATA[${msg.music_url_hq]]></HQMusicUrl>
        <ThumbMediaId><![CDATA[${msg.media_id}]]></ThumbMediaId>
    </Music>
</%block>
