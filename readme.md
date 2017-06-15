AI Story Game for Facebook Messenger

Technical Challenges:
database. chose redis over postgresql for speed, since redis lives on ram memory.

memorize contextual information with each conversation. dont let chat with one impact the other chats.

recognizing text info using reg ex.

ignoring messages sent to kova before she finished speaking: she processes incoming messages after she's done so it seems lk messages that interrupted her were responses to her last ansewrs. solved by checking message time and ignoring things before her last time.

sleeping for hours when i only have 30 sec until timeout. solved through datetime.