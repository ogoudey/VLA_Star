from openai import OpenAI
client = OpenAI()
import asyncio

HOLD_UNITY = True
if HOLD_UNITY:
    image_receiver = None
else:
    import image_receiver

MODEL = "o4-mini"

class VLM:
    def __init__(self, name: str, system_prompt: str, recommendation_system_prompt: str | None = None):
        self.name = name
        self.system_prompt = system_prompt
        self.recommendation_system_prompt = recommendation_system_prompt
        pass

    def status_sync(self, prompt):
        # Wait until image available
        try:
            data_url = image_receiver.get_latest()
        except Exception:
            raise Exception("No latest image found")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{
                "role": "system",
                "content": [
                    {"type": "text", "text": self.system_prompt},
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_url,
                        },
                    },
                ],
            }],
        )
        status = response.choices[0].message.content
        #print(f"{prompt}: {status}")
        return status
    
    async def status(self, prompt):
        try:
            data_url = image_receiver.get_latest()
        except Exception:
            raise Exception("No latest image found")

        def blocking_request():
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system",
                    "content": [
                        {"type": "text", "text": self.system_prompt}
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": data_url
                                }
                            },
                        ],
                    },
                ],
            )
            return response

        response = await asyncio.to_thread(blocking_request)
        return response.choices[0].message.content
    
    async def recommendation(self, prompt):
        try:
            data_url = image_receiver.get_latest()
        except Exception:
            raise Exception("No latest image found")

        def blocking_request():
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system",
                    "content": [
                        {"type": "text", "text": self.recommendation_system_prompt}
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": data_url
                                }
                            },
                        ],
                    },
                ],
            )
            return response

        response = await asyncio.to_thread(blocking_request)
        return response.choices[0].message.content
