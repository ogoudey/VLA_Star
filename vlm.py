from openai import OpenAI
client = OpenAI()

import image_receiver



class VLM:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        pass

    def status(self, prompt):
        # Wait until image available
        try:
            data_url = image_receiver.get_latest()
        except Exception:
            raise Exception("No latest image found")
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
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