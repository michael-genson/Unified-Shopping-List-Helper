import base64
import hashlib
import hmac
import logging

import requests
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_core.utils.request_util import (
    get_account_linking_access_token,
    get_user_id,
)
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard

from ..config import (
    API_APP_CLIENT_ID,
    API_APP_CLIENT_SECRET,
    SHOPPING_LIST_API_LINK_ACCOUNT_ROUTE,
    SHOPPING_LIST_API_UNLINK_ACCOUNT_ROUTE,
)
from ..skill import USL_BASE_URL, sb


def is_cancel_or_stop_request(input: HandlerInput) -> bool:
    return any(
        [
            is_intent_name("AMAZON.CancelIntent")(input),
            is_intent_name("AMAZON.StopIntent")(input),
        ]
    )


@sb.request_handler(can_handle_func=is_request_type("AlexaSkillEvent.SkillAccountLinked"))
def account_linked(input: HandlerInput):
    logging.info("Received new account link event; updating user id")

    user_id = get_user_id(input)
    access_token = get_account_linking_access_token(input)

    if not user_id:
        raise ValueError("Missing user id")

    logging.info(f"user {str(user_id)}")

    if not access_token:
        raise ValueError("Missing access token")

    url = USL_BASE_URL + SHOPPING_LIST_API_LINK_ACCOUNT_ROUTE

    # TODO: wrap this in an interface
    headers = {"Authorization": f"Bearer {str(access_token)}"}
    params = {"userId": user_id}

    r = requests.post(url, headers=headers, params=params)
    r.raise_for_status()


@sb.request_handler(can_handle_func=is_request_type("AlexaSkillEvent.SkillDisabled"))
def skill_disabled(input: HandlerInput):
    logging.info("User has disabled this skill; sending notification to central API")

    user_id = get_user_id(input)

    if not user_id:
        raise ValueError("Missing user id")

    logging.info(f"user {str(user_id)}")

    url = USL_BASE_URL + SHOPPING_LIST_API_UNLINK_ACCOUNT_ROUTE
    hmac_signature = hmac.new(
        key=API_APP_CLIENT_SECRET.encode("utf-8"),
        msg=API_APP_CLIENT_ID.encode("utf-8"),
        digestmod=hashlib.sha256,
    )

    security_hash = base64.b64encode(hmac_signature.digest()).decode()

    # TODO: wrap this in an interface
    headers = {"X-Alexa-Security-Hash": security_hash}
    params = {"userId": user_id}

    r = requests.delete(url, headers=headers, params=params)
    r.raise_for_status()


@sb.request_handler(is_request_type("LaunchRequest"))
def launch_request_handler(input: HandlerInput) -> Response:
    paragraphs = [
        (
            "Welcome to the Unified Shopping List Helper. This skill is designed to integrate the Alexa Shopping List, "
            + "and other To Do lists, with your Unified Shopping List. "
            + "If you're having trouble with this skill, make sure you're properly authenticated in the Alexa app."
        ),
        (
            "To use this skill, add an item to your shopping list the way you would normally do so. There is no need to open this skill. Once your account is linked, and your "
            + "shopping list is configured in the Unified Shopping List, simply add something to your shopping list and it will automatically be synced to your unified list."
        ),
    ]

    if not get_account_linking_access_token(input):
        paragraphs.append(
            (
                "It looks like your account hasn't been linked. Please visit this skill's settings in the Alexa app and link your account. Make sure you've also enabled "
                + "the requested permissions, including access to your shopping list."
            )
        )

    else:
        paragraphs.append(
            "It looks like you've already successfully linked your account to the Unified Shopping List. You may now add things to your shopping list and they will appear on any "
            + 'lists you have configured on the Unified Shopping List. To add something to your shopping list, exit this skill, then say: "Alexa, add apples to my shopping list".'
        )

    speech_text = "\n\n".join(paragraphs)

    input.response_builder.speak(speech_text).set_card(SimpleCard("Welcome!", speech_text)).set_should_end_session(True)
    return input.response_builder.response


@sb.request_handler(is_intent_name("AddToShoppingList"))
def redirect_shopping_list_request(input: HandlerInput) -> Response:
    speech_text = "To add something to your shopping list, please exit this skill and use your normal Alexa shopping list. Please try again after exiting this skill."
    input.response_builder.speak(speech_text).set_card(SimpleCard("Help", speech_text)).set_should_end_session(True)
    return input.response_builder.response


@sb.request_handler(is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(input: HandlerInput) -> Response:
    if get_account_linking_access_token(input):
        speech_text = (
            "It looks like you've already successfully linked your account to the Unified Shopping List. You may now add things to your shopping list and they will appear on any "
            + 'lists you have configured on the Unified Shopping List. To add something to your shopping list, exit this skill, then say: "Alexa, add apples to my shopping list".'
        )

    else:
        speech_text = (
            "It looks like your account hasn't been linked. Please visit this skill's settings in the Alexa app and link your account. Make sure you've also enabled "
            + "the requested permissions, including access to your shopping list."
        )

    speech_text += "If you're still having trouble, make sure you've linked your Alexa shopping list in your Unified Shopping List account."

    input.response_builder.speak(speech_text).set_card(SimpleCard("Help", speech_text)).set_should_end_session(True)
    return input.response_builder.response


@sb.request_handler(is_cancel_or_stop_request)
def cancel_and_stop_intent_handler(input: HandlerInput) -> Response:
    speech_text = ""

    input.response_builder.speak(speech_text).set_card(SimpleCard("Goodbye!", speech_text)).set_should_end_session(True)
    return input.response_builder.response


@sb.exception_handler(can_handle_func=lambda i, e: True)  # type: ignore
def all_exception_handler(input: HandlerInput, ex: Exception) -> Response:
    logging.info("unable to fully process input")
    logging.info(f"{type(ex).__name__}: {ex}")

    speech = "Sorry, I didn't quite catch it. Can you please say it again?"
    input.response_builder.speak(speech).ask(speech)
    return input.response_builder.response
