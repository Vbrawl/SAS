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
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class TemplateArguments:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({', '.join(map(lambda x: x[0]+'='+repr(x[1]), self.__dict__.items()))})"
    
    def toJSON(self) -> dict[str, Any]:
        return self.__dict__