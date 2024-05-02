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
from .TemplateArguments import TemplateArguments



class Template:
    @staticmethod
    def _parse_message(message:str):
        placeholder_marks:list[tuple[int, int, str]] = [] # [(start, end, placeholder-text)]

        while True:
            prevMarkEnd = placeholder_marks[-1][1] if placeholder_marks else 0
            start = message.find("$(", prevMarkEnd)
            if start == -1:
                break

            end = message.find(")", start)
            if end == -1:
                raise ValueError("The template is incomplete.")

            text = message[start+2 : end]
            placeholder_marks.append((start, end, text))
        return placeholder_marks
    
    @staticmethod
    def _compile_message(message:str, marks:list[tuple[int, int, str]], args:TemplateArguments):
        offset = 0
        # marks need to be in ascending order
        for mark in marks:
            if not hasattr(args, mark[2]):
                raise TypeError("args doesn't have all the required attributes.")

            val = getattr(args, mark[2])
            message = message[:offset+mark[0]] + val + message[offset+mark[1]+1:]

            placeholder_len = (mark[1] - mark[0])
            val_len = len(val)
            offset += val_len - placeholder_len - 1
        return message

    def __init__(self, message:str):
        self._message = message
        self._marks = self._parse_message(message)
    
    def compileFor(self, args:TemplateArguments):
        return self._compile_message(self._message, self._marks, args)
    
    def compileWith(self, **kwargs):
        targs = TemplateArguments(**kwargs)
        return self._compile_message(self._message, self._marks, targs)