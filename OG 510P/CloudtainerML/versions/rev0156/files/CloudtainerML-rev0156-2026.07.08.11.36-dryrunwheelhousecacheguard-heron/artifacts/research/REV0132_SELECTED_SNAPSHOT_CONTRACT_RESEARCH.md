# REV0132 selected-snapshot contract research

## Finding

The public evidence lane should not stop at “a digest-verified snapshot exists somewhere.” Hugging Face offline use requires the needed model files to already be cached/downloaded before loading; the Hub cache has concrete `snapshots/<commit>` paths; and Hub download helpers return local cache paths that should be treated as evidence material.

## Applied change

REV0132 binds preflight to capture by writing a shell env file containing the selected digest-verified local snapshot path. The capture wrapper sources that file and refuses to load by ambiguous model-id cache resolution.

## Sources

- https://huggingface.co/docs/transformers/en/installation
- https://huggingface.co/docs/huggingface_hub/en/guides/download
- https://huggingface.co/docs/hub/en/local-cache
- https://huggingface.co/docs/huggingface_hub/en/package_reference/file_download
