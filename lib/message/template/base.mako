<xml>
    <ToUserName><![CDATA[${msg.to_user}]]></ToUserName>
    <FromUserName><![CDATA[${msg.from_user}]]></FromUserName>
    <CreateTime>${msg.timestamp}</CreateTime>
    <MsgType><![CDATA[${msg.msg_type}]]></MsgType>
<%block name="content" />
</xml>
