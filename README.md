# Phenomics Assistant

The [Monarch Initiative](https://monarchinitiative.org/) has an extensive, cross-species, semantic knowledge graph. Phenomics Assistant is a user-friendly interface that uses large language models (LLMs) to enable natural-language interaction with the Monarch KG.

A demo version is available at https://phenomics-assistant.streamlit.app/

## Related repositories

This version of the assistant utilizes [LLM-focused endpoints](https://github.com/monarch-initiative/oai-monarch-plugin) to the main [Monarch API](https://api-v3.monarchinitiative.org/v3/docs), via a Streamlit-based [middleware](https://github.com/oneilsh/kani-utils) to the [Kani](https://github.com/zhudotexe/kani/) LLM framework.