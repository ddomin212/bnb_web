""" This module is used to get travel tips from Bing AI. """
import asyncio
import re

from sydney import SydneyClient


def parse_response(text):
    """
    Parse response text to extract data. This is a helper function for L { get_response }.

    @param text - The text to parse. Should be a string of the response from Bing AI.

    @return The parsed text.
    """
    pattern = re.compile(
        r"^\d+\.\s+(?:(?!\[\^\d+\^\]).)+", re.MULTILINE | re.DOTALL
    )

    matches = pattern.findall(text)

    return matches[0].split("\n")


async def main(text) -> None:
    """
    Asks Bing AI (SydneyClient) for information about the top 10
    places to visit in 50 km range of a location.

    @param text - The location to search for.

    @return The parsed response.
    """
    async with SydneyClient() as sydney:
        response = await sydney.ask(
            f"""What are the top 10 places to visit in 50 km range of: {text},
                                    in numbered list format and without any description.
                                    If you want to include tags, such as 'Historical Landmark',
                                    separate them with the '|' symbol.""",
            citations=False,
        )
        print(response)
        matching = parse_response(response)
        return matching


def get_travel_tips(text):
    """
    This is just an async wrapper for L { main }.

    @param text - text to parse and run

    @return the same thing as L { main }
    """
    return asyncio.run(main(text))
