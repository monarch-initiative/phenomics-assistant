## Implementation Notes - Phenomics Assistant

The version of Phenomics Assistant implemented in this branch utilizes the same functionality as described in this
[bioRxiv preprint](https://www.biorxiv.org/content/10.1101/2024.01.31.578275v1.abstract), including the same API
endpoints, prompts, and tool definitions provided to the model. However, the backing functionality is now provided
by the [Kani](https://github.com/zhudotexe/kani) LLM framework to provide support for additional models, streaming
responses, and other features.

