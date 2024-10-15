# Contributing

## Prerequisites

- [nodejs](https://nodejs.org/en/download/) (only tested with v18)
- [pnpm](https://pnpm.io/) (or npm or yarn)
- [python3](https://www.python.org/downloads/) (and pip)
- [Postman](https://www.postman.com/downloads/) (optional)
  - You can also find the postman json collection here: [TinyGen.postman_collection.json](./assets/TinyGen.postman_collection.json)
  - You can run the postman collection in [this page](https://rami-maalouf.postman.co/workspace/Team-Workspace~c0c74318-5842-4cca-8c8b-00f362d73874/collection/23796705-0b576e90-c2c1-4875-983f-1f6839012fb0?action=share&creator=23796705)
    - Alternatively, you can run the fastAPI-generated openapi docs from [this page](https://tiny-gen.vercel.app/api/docs)

- run `pnpm i` in the root folder to install all the node dependencies.
- create a virtual environment with `python3 -m venv .venv` and activate it with `source venv/bin/activate` then run `pip install -r requirements.txt` to install all the python dependencies.
- run `cp .env.example .env` to create a `.env` file and fill in the required environment variables.

## Development

### Chrome Extension

To run the browser extension, run `pnpm dev:plasmo` in the root folder, then you will find the extension in the `build/chrome-mv3-dev` folder. You can then load the extension in chrome by going to `chrome://extensions` and clicking on `Load unpacked` and selecting that folder.

To also run the backend alongside the extension, alternatively run `pnpm dev` in the root folder, this will start the Next.js and the FastAPI server as well as the extension.

### Firefox Extension

To run the browser extension, run `pnpm dev:plasmo --target=firefox-mv3` in the root folder, then you will find the extension in the `build/firefox-mv3-dev` folder. You can then load the extension in firefox by going to `about:debugging` and clicking on `This Firefox` and then `Load Temporary Add-on...` and selecting the `manifest.json` file in that folder.

To also run the backend alongside the extension, run `pnpm dev:backend` in the root folder as well (in another terminal), this will start the Next.js and the FastAPI server.

You can also run each backend separately by running `pnpm dev:next` and `pnpm dev:fastapi` in the root folder.

### Edge Extension

To run the browser extension, run `pnpm dev:plasmo --target=edge-mv3` in the root folder, then you will find the extension in the `build/edge-mv3-dev` folder. You can then load the extension in edge by going to `edge://extensions` and clicking on `Load unpacked` and selecting that folder.

To also run the backend alongside the extension, run `pnpm dev:backend` in the root folder as well (in another terminal), this will start the Next.js and the FastAPI server.

You can also run each backend separately by running `pnpm dev:next` and `pnpm dev:fastapi` in the root folder.

## Production

To build the extension for production, run `pnpm build:plasmo` in the root folder, then you will find the extension in the `build/<browser>-mv3-prod` folder.

By default, the extension will be built for chrome, but you can change that by passing the `--target` flag with the browser name and version you want to build for (e.g: `pnpm build:plasmo --target=firefox-mv3`).

To zip the extension, simply add the `--zip` flag (e.g: `pnpm build:plasmo --target=firefox-mv3 --zip`).

## Testing

Oh, just realized that I haven't added any tests yet. I'll add them someday... maybe.
