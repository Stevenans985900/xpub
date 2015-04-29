import os
from nose.tools import raises
from .main import Prompt, Prompter

# valid prompt dicts of various types for testing
valid_prompt_dicts = {

     # example of dict to prompt the user for open-ended input
     'study': {  
        "key": "name",
        "text": "Name of study?",
        "info": "Your study name should only consist of alphanumeric characters and underscores.",
        "example": "pig_chewing_study",
        "require": True,
        "type": "open",
        "enum": [],
        "store": [
            "xromm"
        ],
        "regex": "\\w{3}"
    },

    # example of dict to prompt the user to choose from an enumerated list
    'leader': {
        "key": "leader",
        "text": "Name of study leader?",
        "info": "Specify the lab member most responsible for conducting this study.",
        "example": "Kazutaka Takashi",
        "require": True,
        "type": "enum_open",
        "enum": [                   # list of options to be enumerated
            "Callum Ross",
            "Kazutaka Takashi"
        ],
        "store": [
            "xromm"
        ],
        "regex": "^\\d$"
    },

    # example of dict that prompts the user to choose yes or no
    'public': {
        "key": "meta_public",
        "text": "Metadata for this study is public?",
        "info": "Can the metadata for this study be made publicly available?",
        "example": True,        # json value should be `true` (lowercase)
        "require": True,
        "type": "bool",
        "enum": [],
        "store": [
            "xromm"
        ],
        "regex": ""
    }
}

def test_valid_prompts():
    '''Testing Prompt class'''
    prompt = Prompt(valid_prompt_dicts['study'])
    assert prompt.key is "name"
    assert prompt.type is "open"
    assert prompt.require is True
    result = prompt(testing=True)
    assert result == "pig_chewing_study", "should return example when testing"

    prompt = Prompt(valid_prompt_dicts['leader'])
    assert prompt.key is "leader"
    assert prompt.type is "enum_open"
    assert prompt.require is True
    result = prompt(testing=True)
    assert result == "Kazutaka Takashi", "should return example when testing"

    prompt = Prompt(valid_prompt_dicts['public'])
    assert prompt.key is "meta_public"
    assert prompt.type is "bool"
    assert prompt.require is True
    result = prompt(testing=True)
    assert result == prompt.example, "should return example when testing"

@raises(KeyError)
def test_missing_key():
    '''
    Testing prompt dict for required keys: KeyError expected.
    
    This prompt dict is missing an `example` key.

    '''
    d = {
        "key": "foo",
        "text": "Do you feel the foo?",
        "info": "",
        "type": "bool",
        "store": ["xromm"],
        "require": True
    }
    Prompt(d)                   # should raise KeyError
    
@raises(ValueError)
def test_invalid_type():
    '''Testing for invalid prompt type: ValueError expected'''
    d = {
        "key": "foo",
        "text": "What is the foo?",
        "info": "",
        "example": "bar",
        "type": "foo",          # `foo` is not a valid prompt type
        "store": ["xromm"],
        "require": True
    }
    Prompt(d)                   # should raise ValueError
    
@raises(ValueError)
def test_invalid_store():
    '''Testing for invalid store value: ValueError expected'''
    d = {
        "key": "foo",
        "text": "Do you feel the foo?",
        "info": "",
        "example": True,
        "type": "bool",         # `bool` is a valid prompt type
        "store": ["foo_db"],    # but `foo_db` is not a valid store value
        "require": True
    }
    Prompt(d)                   # should raise ValueError
    
def test_prompter():
    '''
    Testing a Prompter instance.

    Note that when testing a prompter, the returned input values
    are just the example values given in the specified config file,
    For example, if prompting for a new study resource we'd use
    the `config/study.json` file to configure the prompter:

        {
            "key": "name",
            "text": "Name of study?",
            "example": "pig_chewing_study",     # input value to return
            ...                                 # when testing
        },
        {
            "key": "leader",
            "text": "Name of study leader?",
            "example": "Kazutaka Takashi",      # input value when testing
            ...
        },

    '''
    # this is the expected result based on the example inputs specified 
    # in our `study.json` config file
    expected = {
        "data": {
            "name": "pig_chewing_study", 
            "notes": "See `http://github.com/rcc-uchicago/xpub` for more info.", 
            "data_public": False, 
            "meta_public": True, 
            "pi": "Callum Ross", 
            "leader": "Kazutaka Takashi", 
            "desc": "A study that looks at how pigs chew stuff."
        }, 
        "version": "0.0.1", 
        "resource": "study"
    }

    d = os.path.dirname(os.path.realpath(__file__))
    local_config_path = os.path.join(d, '..', 'config', 'study.json')
    CONFIG_DIR = os.environ.get('XROMM_CONFIG', local_config_path)
    prompt = Prompter(CONFIG_DIR, testing=True)
    prompt()
    assert prompt.results == expected
