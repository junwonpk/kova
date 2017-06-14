AI Story Game for Facebook Messenger

Technical Challenges:
database. chose redis over postgresql for speed, since redis lives on ram memory.

memorize contextual information with each conversation. dont let chat with one impact the other chats.

recognizing text info using reg ex.

getting around heroku 30 sec timeout

ignoring messages sent to kova before she finished speaking: she processes incoming messages after she's done so it seems lk messages that interrupted her were responses to her last ansewrs. solved by checking message time and ignoring things before her last time.