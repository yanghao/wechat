<%inherit file="base.mako" />

<%block name="content">
    <Video>
        <MediaId><![CDATA[${msg.media_id}]]></MediaId>
        <Title><![CDATA[${msg.media_title}]]></Title>
        <Description><![CDATA[${msg.media_desc}]]></Description>
    </Video>
</%block>
