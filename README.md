# Generative Audio Extensions (GAE) - .gaeMaker and .gaePlayer

**Generative Audio Extensions** is a set of open-source tools that allow you to create and play generative audio compositions. This project includes:

- **.gaeMaker:** A tool to create generative audio compositions by layering audio files.
- **.gaePlayer:** A player to load and play generative audio compositions created with .gaeMaker.
- **.gaeExtract:** A tool to extract files made with .gaeMaker.

## gaeMaker

`gaeMaker` is a tool that enables you to create generative audio compositions by combining multiple audio layers. Here's how it works:

### Features

- Create a new project by specifying a file name and various composition details.
- Add audio layers to your composition by selecting the layer directories.
- Include metadata such as duration, BPM, key, artist, and track name.
- Add cover art to your composition.
- Generate a `.gae` file containing your composition.

### Usage

1. Run `gaeMaker`.
2. Provide a name for your project and set the composition details.
3. Add audio layers by selecting their respective directories.
4. Add metadata and cover art.
5. Click "Create .gae File" to generate the composition.

## gaePlayer

`gaePlayer` is a player that allows you to load and play generative audio compositions created with `gaeMaker`. Here's how it works:

### Features

- Load a `.gae` composition file.
- Generate a random composition by shuffling and layering the audio files.
- Play the composition with metadata display.
- Stop the composition and clean up the temporary files.

### Usage

1. Run `gaePlayer`.
2. Click "Browse" to select a `.gae` composition file created with `gaeMaker`.
3. Click "Generate Random Composition" to play a random arrangement of the audio layers.
4. Metadata and cover art are displayed during playback.
5. Click "Stop Composition" to halt playback and delete the temporary files.

## gaeExtract

`gaeExtract` is a tool designed for extracting files from compositions created with `gaeMaker`. This tool can be useful for extracting and reusing audio layers, cover art, or other assets from existing `.gae` files.

### Features

- Extract files from `.gae` composition files.
- Reuse extracted audio layers, cover art, or other assets in new compositions.
- Organize and manage extracted assets.

### Usage

1. Run `gaeExtract`.
2. Select a `.gae` composition file.
3. Choose the files you want to extract from the composition.
4. Click "Extract" to copy the selected files to a destination directory.

Feel free to contribute to this project and explore the endless possibilities of generative audio compositions with GAE.

## Getting Started

To get started with this project, follow the installation and usage instructions for each tool (`gaeMaker`, `gaePlayer`, and `gaeExtract`) in their respective directories.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Special thanks to the open-source community for their contributions.
- Enjoy creating and playing generative audio compositions with GAE!
