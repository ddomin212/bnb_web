from sydney import SydneyClient
import asyncio
import re


def parse_response(text):
    pattern = re.compile(
        r'^\d+\.\s+(?:(?!\[\^\d+\^\]).)+', re.MULTILINE | re.DOTALL)

    matches = pattern.findall(text)

    return matches[0].split("\n")


async def main(text) -> None:
    async with SydneyClient() as sydney:
        response = await sydney.ask(f"""What are the top 10 places to visit in 50 km range of: {text}, 
                                    in numbered list format and without any description. If you want to include tags, such as
                                    'Historical Landmark', separate them with the '|' symbol.""", citations=False)
        print(response)
        matching = parse_response(response)
        return matching


def get_travel_tips(text):
    return asyncio.run(main(text))
