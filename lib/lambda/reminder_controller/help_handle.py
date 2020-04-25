return {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': 'Fulfilled',
            'message': {
                'contentType': 'PlainText',
                'content': msg
            },
            'responseCard': {
                'version': '0',
                'contentType': 'application/vnd.amazonaws.card.generic',
                'genericAttachments': [{
                    'title': 'title1',
                    'subTitle': 'subtitle',
                    "buttons":[ 
                        {
                            "text":"button 1",
                            "value":"value 1"
                        },
                        {
                            "text":"button 2",
                            "value":"value 2"
                        },
                        {
                            "text":"button 3",
                            "value":"value 3"
                        }]
                }]
            }
        }
    }