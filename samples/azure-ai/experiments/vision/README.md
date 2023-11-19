# Experimenting with Azure AI Vision

## Prerequisites

### Azure Resources

* Azure AI Vision (check regional avaiability for v4 preview features)
* Azure Cognitive Search
* Azure OpenAI

### Stage Data

If you have your own, great. If not, NGA.

Single index with everything...
Expected index schema:
```json
/* TODO */
{
  fields: [
    id imageIdentifier,
    bytes imageData,
    string imageCaption,
    string[] imageTags,
    float[] vectorizedImage,
    float[] vectorizedImageMetadata # text from caption/tags
  ]
}
```

Multi-indexes merged (one with vectorizedImage, one with vectorizedImageMetadata)

### Experiments

Search for the best image(s) to match a given text/language-based request.

| Lexical over Image Metadata | Image Vector | Image Metadata Vector | Semantic Re-Rank | Observations |
|---------|--------------|-----------------------|------------------|--------------|
| :heavy_check_mark: | | | | [Link]() |
| :heavy_check_mark: | | | :heavy_check_mark: | [Link]() |
| | :heavy_check_mark: | | | [Link]() |
| | :heavy_check_mark: | | :heavy_check_mark: | [Link]() |
| | | :heavy_check_mark: | | [Link]() |
| | | :heavy_check_mark: | :heavy_check_mark: | [Link]() |
| :heavy_check_mark: | :heavy_check_mark: | | | [Link]() |
| :heavy_check_mark: | :heavy_check_mark: | | :heavy_check_mark: | [Link]() |
| :heavy_check_mark: | | :heavy_check_mark: | | [Link]() |
| :heavy_check_mark: | | :heavy_check_mark: | :heavy_check_mark: | [Link]() |
| :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | | [Link]() |
| :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | [Link]() |
