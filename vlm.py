from openai import OpenAI
client = OpenAI()
import asyncio

USE_UNITY = False
if USE_UNITY:
    import image_receiver
else:
    image_receiver = None

    

USE_WEBCAM = True
if USE_WEBCAM:
    import webcam as image_receiver

    

MODEL = "o4-mini"

class VLM:
    def __init__(self, name: str, system_prompt: str, recommendation_system_prompt: str | None = None):
        self.name = name
        self.system_prompt = system_prompt
        self.recommendation_system_prompt = recommendation_system_prompt
        pass

    def status_sync(self, prompt):
        print(f"Getting status... for {prompt}")
        # Wait until image available
        try:
            data_url = image_receiver.get_latest()
        except Exception:
            raise Exception("No latest image found")
        print("Sending completion...")
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
        print(f"{prompt}: {status}")
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
