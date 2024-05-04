'''
Copyright 2024 Jim Konstantos <konstantosjim@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This file (Constants.py) contains some constant-values and built-in settings
for the "Daemon" component of the project (SAS).
'''
from sas_commons.templates.PersonTemplateArguments import PersonTemplateArguments


def test_PersonTemplateArguments_init():
    pta = PersonTemplateArguments(telephone="+19999999999")
    assert getattr(pta, "telephone", None) == "+19999999999"
    assert not hasattr(pta, "id")

    pta = PersonTemplateArguments(telephone="+19999999999", first_name="John")
    assert getattr(pta, "first_name", None) == "John"