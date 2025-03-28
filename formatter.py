import model


def normalize_whitespace_in_arguments_list(code: model.Component):
    for element in code.iterate(types=[model.ElementsList]):
        element: model.ElementsList

        for i, token in enumerate(element.elements_list):
            # Children 1, 3, ... are whitespace and delimiters.
            if i % 2 == 0:
                continue
            token: str = token
            token = token.strip(" \n\t.")  # Remove whitespace and "..." line break ellipsis surrounding delimiter.
            token += " "  # Add single space after delimiter.
            element.elements_list.children[i] = token


def normalize_whitespace_in_parenthesized(code: model.Composite):
    types = [model.Parenthesized]
    for element in code.iterate(types):
        element: model.Parenthesized
        for index in [1, 3]:
            element.children[index] = ""


def normalize_whitespace_in_assignment(code: model.Component):
    """Ensure equality sign of assignment is surrounded by single spaces."""
    types = [model.OutputArguments]
    for element in code.iterate(types):
        element: model.OutputArguments
        for index in [1, 3]:
            element.children[index] = " "


def remove_semicolon_after_end_keyword(code: model.Component):
    """Remove optional semicolon after the an 'end' keyword."""
    types = [model.Block]
    for element in code.iterate(types):
        element: model.Block
        if element.children[-1] == ";":
            element.children[-1] = ""


def remove_semicolon_after_if_condition(code: model.Component):
    for element in code.iterate([model.If]):
        if element.head.children[-1] == ";":
            element.head.children[-1] = ""


def remove_semicolon_after_keyword(code: model.Component):
    for element in code.iterate([model.Statement]):
        core = element.children[-3]
        if isinstance(core, model.Leaf) and core.value in ["return", "break", "continue"]:
            element.children[-2] = ""
            element.children[-1] = ""
            core._successor = element.children[-2]


def remove_white_space_before_semicolon(code: model.Component):
    for element in code.iterate(types=[model.Statement]):
        if element.children[-2] == "":
            continue
        element.children[-2] = ""
        element.children[-3]._successor = element.children[-2]


def set_context(element: model.Component):
    for i, child in enumerate(element):
        if not isinstance(child, model.Component):
            continue

        child._predecessor = element.children[i-1] if i > 0 else None
        child._successor = element.children[i+1] if i < len(element) - 1 else None
        child.parent = element

        set_context(child)


def normalize_indentation(element: model.Component):

    for element, level in element.iterate_with_indent():

        if (
                not isinstance(element, model.Construct)
                and (not isinstance(element, model.Leaf) or element.value not in ["end", "elseif", "else"])
        ):
            continue

        element_is_block_head = (
                element.parent
                and isinstance(element.parent, model.Block)
                and type(element.parent.head) == type(element)
                and element.parent.head == element
        )
        if element_is_block_head:
            continue

        indent = level * 4 * " "

        if element.predecessor is not None:
            assert type(element.predecessor) == str
            new: str = element.predecessor.rstrip(" ")
            if not new.endswith("\n"):
                new += "\n"

            element.predecessor = new + indent

        elif element.parent is not None and element.parent.predecessor is not None:
            assert type(element.parent.predecessor) == str
            element.parent.predecessor = "\n" + indent


def ensure_function_end(element: model.Component):
    """Ensure function block ends with 'end' keyword."""
    for element in element.iterate(types=[model.Function]):
        if element.children[5] == "":
            element.children[5] = "\n"
        element.children[6] = "end"


def normalize_trailing_whitespace(file: model.File):
    """Remove all trailing whitespace in a file and add a newline."""
    file[2] = "\n"


def normalize_leading_whitespace(file: model.File):
    """Remove all leading whitespace in a file."""
    file[0] = ""


def ensure_empty_line_before_comment(element: model.Component):
    """Ensures an empty line before each block of comments."""
    for element in element.iterate(types=[model.Comment]):
        if element.predecessor is None:
            continue
        assert type(element.predecessor) == str

        parent = element.parent
        i_element = parent.index_of(element)

        if isinstance(parent[i_element-2], model.Comment):
            continue

        if element.predecessor.count("\n") < 2:
            parent[i_element-1] = "\n" + element.predecessor
            # TODO: fix relationships






