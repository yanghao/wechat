<%inherit file="base.mako" />

<%block name="content">
    <Video>
        <MediaId><![CDATA[${msg.content.media_id}]]></MediaId>
        <Title><![CDATA[${msg.content.media_title}]]></Title>
        <Description><![CDATA[${msg.content.media_desc}]]></Description>
    </Video>
</%block>
