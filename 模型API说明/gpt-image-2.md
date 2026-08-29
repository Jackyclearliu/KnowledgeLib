# Generations（Image generation）

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /v1/images/generations:
    post:
      summary: Generations（Image generation）
      deprecated: false
      description: >-
        ### 1. Function Introduction

        Generate one or more high-quality images based on text prompts,
        supporting:

        - GPT-Image Series Models (gpt-image-1.5 / gpt-image-1 /
        gpt-image-1-mini)

        - Fine-grained control over multi-size, multi-quality, transparent
        background, streaming output, etc.

        - Comes with built-in content moderation, allowing customizability of
        moderation strictness 

        - Asynchronous / Synchronous dual mode, adaptable to different business
        scenarios 


        ### 2. Request Parameters

        | Field | Type | Required | Description | Remarks |

        |---|---|---|---|------|

        | prompt | string | ✅ | Description text | Length ≤ 32k (gpt-image-1.5)
        |

        | model | string | ✅ | Model | Optional: gpt-image-1.5 / gpt-image-1 /
        gpt-image-1-mini |

        | n | int |  | Number of images to generate | 1-10; dall-e-3 only
        supports 1 |

        | size | string |  | Dimensions | 1024x1024, 1536x1024 (landscape),
        1024x1536 (portrait), auto. When the dimension selection is `auto`, the
        model will automatically provide the optimal ratio based on the prompt.|

        | quality | string |  | Quality | low / medium / high / auto |

        | background | string |  | Background | transparent / opaque / auto |

        | output_format | string |  | Output format | png / jpeg / webp |

        | output_compression | int |  | Compression ratio | 0-100; only
        effective for jpeg/webp |

        | moderation | string |  | moderation strictness | low (lenient) / auto
        |

        | stream | bool |  | Streaming output | Only supported by the GPT-Image
        series |

        | partial_images | int |  | Number of streaming shards | 0-3; 0 = only
        return the final image |

        | async | query |  | Whether asynchronous | Returns task_id when passing
        `?async=true` |


        ### 3. Precautions

        - ✅ Please strictly adhere to the prompt character length limit
        according to the selected model

        - 📏 Different models support different size and quality parameters, so
        compatibility needs to be confirmed in advance

        - 🔒 Sensitive content will be intercepted by the system, and it is
        recommended to keep the moderation parameter in the default auto mode

        - 📊 Pricing is calculated based on the Tokens of the generated images,
        with different models/qualities consuming different amounts of Tokens
        (see the Pricing section for details)

        - 🔄 The generation progress of asynchronous tasks can be actively
        checked via the task query interface


        ### 4. Price

        | Model | Text Input | Text Output | Image Output | Remarks |

        |------|--------------|------|--------|------|

        | gpt-image-1 | 5 PTC/1M Tokens | |40 PTC/1M Tokens | High-quality model
        |

        | gpt-image-1-mini | 2 PTC/1M Tokens | |8 PTC/1M Tokens | Efficient and
        Economical Model |

        | gpt-image-1.5 | 5 PTC/1M Tokens | 10 PTC/1M Tokens | 32 PTC/1M Tokens
        | Balanced Model |


        > The final price shall be based on the number of Tokens consumed as
        returned by the request 

        gpt-image-1: Price Reference

        ![image.png](https://api.apifox.com/api/v1/projects/4012774/resources/518894/image-preview)
      tags:
        - Default module/Image Generation/GPT-Image Series
      parameters:
        - name: response_format
          in: query
          description: >-
            URL or original base64 format. The return format for images
            generated using DALL-E 2 and DALL-E 3. This parameter is not
            supported by the GPT-Image model, which always returns
            base64-encoded images.
          required: false
          example: url
          schema:
            type: string
        - name: async
          in: query
          description: Whether to return images asynchronously
          required: false
          example: 'false'
          schema:
            type: string
        - name: Authorization
          in: header
          description: ''
          required: false
          example: Bearer {{YOUR_API_KEY}}
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                prompt:
                  type: string
                  title: ''
                  description: >-
                    A text description of the required image. The more detailed
                    the description, the better the expected result.

                    **Character length limits:**

                    - GPT-Image series models: maximum 32000 characters

                    - DALL-E-2: maximum 1000 characters

                    - DALL-E-3: maximum 4000 characters


                    **Writing suggestions:**

                    - Include the subject (e.g., "baby sea otter"), action
                    (e.g., "playing"), scene (e.g., "in the ocean waves")

                    - Specify the style (e.g., "watercolor style"), lighting
                    (e.g., "soft light"), and color (e.g., "blue and white")

                    - Avoid vague descriptions; use specific words to improve
                    generation accuracy.
                size:
                  type: string
                  description: >-
                    The generated image size varies depending on the model:

                    - GPT-Image series: 1024x1024, 1536x1024 (landscape),
                    1024x1536 (portrait), auto (automatic adaptation)

                    - DALL-E-2: 256x256, 512x512, 1024x1024

                    - DALL-E-3: 1024x1024, 1792x1024 (landscape), 1024x1792
                    (portrait)
                  title: ''
                  enum:
                    - 1024x1024
                    - 1536x1024
                    - 1024x1536
                    - auto
                  x-apifox-enum:
                    - value: 1024x1024
                      name: ''
                      description: ''
                    - value: 1536x1024
                      name: ''
                      description: ''
                    - value: 1024x1536
                      name: ''
                      description: ''
                    - value: auto
                      name: ''
                      description: ''
                  default: auto
                background:
                  type: string
                  description: >-
                    Image background settings, applicable only to GPT-Image
                    series models:

                    - transparent: Transparent background (PNG/WEBP format only
                    supported)

                    - opaque: Opaque background

                    - auto: Automatic judgment (default, intelligently set
                    according to prompt word scenario)


                    Note: When transparent is selected, output_format must be
                    set to png or webp
                  enum:
                    - transparent
                    - opaque
                    - auto
                  x-apifox-enum:
                    - value: transparent
                      name: ''
                      description: ''
                    - value: opaque
                      name: ''
                      description: ''
                    - value: auto
                      name: ''
                      description: ''
                  default: auto
                moderation:
                  type: string
                  description: >-
                    Content moderation level, controlling the compliance of
                    generated images:

                    - low: lenient moderation, allowing slight creative
                    expression

                    - auto: automatic moderation (default), balancing compliance
                    and creativity
                  enum:
                    - low
                    - auto
                  x-apifox-enum:
                    - value: low
                      name: ''
                      description: ''
                    - value: auto
                      name: ''
                      description: ''
                'n':
                  type: integer
                  description: >-
                    Number of images generated:

                    - Value range: 1-10 (GPT-Image/DALL-E-2)

                    - DALL-E-3 only supports n=1


                    Note: The more images generated, the more tokens are
                    consumed and the longer the generation time
                  minimum: 1
                  maximum: 10
                  default: 1
                quality:
                  type: string
                  enum:
                    - auto
                    - high
                    - medium
                    - low
                  x-apifox-enum:
                    - value: auto
                      name: ''
                      description: ''
                    - value: high
                      name: ''
                      description: ''
                    - value: medium
                      name: ''
                      description: ''
                    - value: low
                      name: ''
                      description: ''
                  default: auto
                  description: >-
                    The generated image quality. 'auto' (default) will
                    automatically select the best quality for the given model.

                    - GPT-Image model: Supports high, medium, and low modes.

                    - DALL-E-3: Supports hd and standard image quality.

                    - DALL-E 2: Only standard can be selected.
                model:
                  type: string
                  enum:
                    - gpt-image-1
                    - gpt-image-1-mini
                    - gpt-image-1.5
                  x-apifox-enum:
                    - value: gpt-image-1
                      name: ''
                      description: ''
                    - value: gpt-image-1-mini
                      name: ''
                      description: ''
                    - value: gpt-image-1.5
                      name: ''
                      description: ''
                  default: gpt-image-1.5
                output_compression:
                  type: integer
                  description: >-
                    Image compression level (GPT-Image only, default 100):

                    - Value range: 0-100 (percentage)

                    - 0: No compression (largest file size, best quality)

                    - 100: Maximum compression (smallest file size, quality may
                    be compromised)


                    Only applicable to webp/jpeg formats, png format does not
                    support compression
                  minimum: 0
                  maximum: 100
                  default: 100
                output_format:
                  type: string
                  description: >-
                    Image output format (GPT-Image only):

                    - png: Supports transparent backgrounds, lossless
                    compression

                    - jpeg: Good compatibility, smaller file size

                    - webp: Balances compression and quality, supports
                    transparency


                    When selecting transparent background, png or webp format
                    must be used
                  enum:
                    - webp
                    - png
                    - jpeg
                  x-apifox-enum:
                    - value: webp
                      name: ''
                      description: ''
                    - value: png
                      name: ''
                      description: ''
                    - value: jpeg
                      name: ''
                      description: ''
                  default: png
                partial_images:
                  type: integer
                  description: >-
                    Number of partial images generated (GPT-Image only):

                    - Value range: 0-3

                    - 0: Do not return partial images, return the complete image
                    after generation (default)

                    - 1-3: Return partial image previews in stages, and finally
                    return the complete image


                    Only effective when stream=true, suitable for scenarios that
                    require fast preview
                  default: 0
                stream:
                  type: boolean
                  description: >-
                    Enable streaming generation (GPT-Image only):

                    - false (default): Return all data at once after generation

                    - true: Return image data in stages as streaming events


                    Combined with the partial_images parameter, progressive
                    image preview can be achieved
                  default: false
              required:
                - prompt
                - model
              x-apifox-orders:
                - model
                - prompt
                - size
                - background
                - moderation
                - 'n'
                - quality
                - output_compression
                - output_format
                - partial_images
                - stream
            example:
              prompt: A cute baby sea otter
              model: gpt-image-1.5
              size: 1024x1024
              'n': 1
              background: auto
              moderation: auto
              output_format: png
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties:
                  background:
                    type: string
                  created:
                    type: integer
                  data:
                    type: array
                    items:
                      type: object
                      properties:
                        url:
                          type: string
                      x-apifox-orders:
                        - url
                  output_format:
                    type: string
                  quality:
                    type: string
                  size:
                    type: string
                  usage:
                    type: object
                    properties:
                      input_tokens:
                        type: integer
                      input_tokens_details:
                        type: object
                        properties:
                          image_tokens:
                            type: integer
                          text_tokens:
                            type: integer
                        required:
                          - image_tokens
                          - text_tokens
                        x-apifox-orders:
                          - image_tokens
                          - text_tokens
                      output_tokens:
                        type: integer
                      output_tokens_details:
                        type: object
                        properties:
                          image_tokens:
                            type: integer
                          text_tokens:
                            type: integer
                        required:
                          - image_tokens
                          - text_tokens
                        x-apifox-orders:
                          - image_tokens
                          - text_tokens
                      total_tokens:
                        type: integer
                    required:
                      - input_tokens
                      - input_tokens_details
                      - output_tokens
                      - output_tokens_details
                      - total_tokens
                    x-apifox-orders:
                      - input_tokens
                      - input_tokens_details
                      - output_tokens
                      - output_tokens_details
                      - total_tokens
                required:
                  - background
                  - created
                  - data
                  - output_format
                  - quality
                  - size
                  - usage
                x-apifox-orders:
                  - background
                  - created
                  - data
                  - output_format
                  - quality
                  - size
                  - usage
          headers: {}
          x-apifox-name: Success
      security: []
      x-apifox-folder: Default module/Image Generation/GPT-Image Series
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/5037766/apis/api-290106862-run
components:
  schemas: {}
  securitySchemes: {}
servers:
  - url: https://api.302.ai
    description: Production Environment
security: []

```
