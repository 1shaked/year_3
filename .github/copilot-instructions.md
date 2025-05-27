# Code Style Guide for Copilot

---------------

## In JS and TS files
- **File Length**: Limit files to 150 lines unless approved.
- **Function Length**: No single function should exceed 30 lines without approval.
- **Component Creation**: Always define an `interface` for component props, use regular functions for components, and avoid using arrow functions.
- **Interface Naming**: Interface names must end with `Interface` (e.g., `UserPropsInterface`).
- **Data Validation**: Validate all server data using Zod's safe parse.
- **Props Passing**: Do not pass props solely for forwarding them to a child component.
- **Variable Declaration**: Prefer `const`; use `let` only when mutation is required.
- **Avoid `any`**: Explicitly type all variables and function signatures—never use `any`.
- **Component Documentation**: Use JSDoc for documenting all new components.
- **Data Fetching**: Use React Query or Redux with async thunk for fetching data.
- **Library Typing**: Always define appropriate types when using libraries (e.g., Redux, React Query, Jotai).
- **State Logic**: If state logic becomes complex, abstract it into a custom hook.
- **Avoid Duplication**: Do not copy-paste logic—create reusable hooks instead.
- **Array Operations**: Only use `.map()` when returning a transformed array.
- **Exports**: Prefer named exports (`export`) over default exports.
- **File Paths**: Use alias imports; use relative imports only within the same directory.
- **Help Policy**: If stuck more than one hour beyond expectations, request help.
- **Type Files**: Define types in `.d.ts` files.
- **Types Organization**: Store type definitions in a dedicated `types/` folder if they are numerous.
- **Constants**: Define constants in uppercase with underscores (e.g., `MAX_RETRIES`) and add `as const`.
- **Props**: Do not destructure props in the function signature.
---

## Props Restrictions

- Avoid passing components as props unless absolutely necessary.
- Avoid passing functions as props unless essential. Always include full typings.

---

## Additional Guidelines

- **Complex Functions**: Document complex logic using JSDoc comments.
- **Spelling**: Use a spell-checker extension to prevent typos in code and comments.
- **Component Design**: Consult Shaked before abstracting new components.
- **Global Variables**: Avoid global variables unless approved by Shaked.


----------

## For Python Files
- **File Length**: Limit files to 150 lines unless approved.
- **Function Length**: No single function should exceed 30 lines without approval.
- **Variable Declaration**: Use the snake_case convention for variable names.
- **Type Annotations**: Use type annotations for all function signatures.
- **Docstrings**: Write docstrings for all public modules, functions, and classes.
- **Imports**: Organize imports in the following order: standard library, third-party libraries, local imports.
- **Function Naming**: Use snake_case for function names.
- **Class Naming**: Use CamelCase for class names.
- **Avoid Global Variables**: Do not use global variables unless absolutely necessary.
- **Error Handling**: Use exceptions for error handling instead of return codes.
- **Constants**: Define constants in uppercase with underscores (e.g., `MAX_RETRIES`).
