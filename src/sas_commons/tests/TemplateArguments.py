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
'''
from sas_commons.templates import TemplateArguments
import pytest


def test_TemplateArguments__init(self):
    ta = TemplateArguments(a=2, b=3)
    assert ta.a == 2 # type: ignore
    assert ta.b == 3 # type: ignore
    with pytest.raises(ValueError): ta.c == 4 # this doesn't exist and we know it
    with pytest.raises(ValueError): ta.d == 5 # this doesn't exist and we know it

    ta2 = TemplateArguments(c=4, d=5)
    with pytest.raises(ValueError): ta2.a == 2 # this doesn't exist and we know it
    with pytest.raises(ValueError): ta2.b == 3 # this doesn't exist and we know it
    assert ta2.c == 4 # type: ignore
    assert ta2.d == 5 # type: ignore