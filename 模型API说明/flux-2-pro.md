# Flux-2-Pro (generates images)

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /flux/v1/flux-2-pro:
    post:
      summary: Flux-2-Pro (generates images)
      deprecated: false
      description: >
        Official documentation:
        https://api.bfl.ml/scalar#tag/tasks/POST/v1/flux-pro

        Please refer to the official documentation; all parameters are
        consistent with the official documentation.


        Official pricing: https://docs.bfl.ml/pricing/


        **Steps for using the interface:**

        1.Use the video generation interface (/flux/v1/flux-2-pro), fill in the
        corresponding parameters, and obtain the task ID.

        2.Use the query interface (/flux/v1/get_result) and fill in the task ID
        to obtain the result.


        **Price: Input (reference images): 0.015 PTC per megapixel. 

        Output: First megapixel is 0.03 PTC, then 0.015 PTC per additional
        megapixel.**
      tags:
        - Default module/Image Generation/Flux
      parameters:
        - name: Authorization
          in: header
          description: ''
          required: true
          example: Bearer {{YOUR_API_KEY}}
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              title: Flux2Inputs
              type: object
              properties:
                prompt:
                  type: string
                  title: Prompt
                  description: Text prompt for image generation.
                  examples:
                    - ein fantastisches bild
                input_image:
                  type: string
                  title: Input Image
                  description: Path to the input image.
                input_image_2:
                  type: string
                  title: Input Image 2
                  description: Path to the second input image.
                input_image_3:
                  type: string
                  title: Input Image 3
                  description: Path to the third input image.
                input_image_4:
                  type: string
                  title: Input Image 4
                  description: Path to the fourth input image.
                input_image_5:
                  type: string
                  title: Input Image 5
                  description: >-
                    Base64 encoded image or URL to use with Kontext.
                    *Experimental Multiref*
                input_image_6:
                  type: string
                  title: Input Image 6
                  description: >-
                    Base64 encoded image or URL to use with Kontext.
                    *Experimental Multiref*
                input_image_7:
                  type: string
                  title: Input Image 7
                  description: >-
                    Base64 encoded image or URL to use with Kontext.
                    *Experimental Multiref*
                input_image_8:
                  type: string
                  title: Input Image 8
                  description: >-
                    Base64 encoded image or URL to use with Kontext.
                    *Experimental Multiref*
                seed:
                  type: integer
                  title: Seed
                  description: Optional seed for reproducibility.
                  examples:
                    - 42
                width:
                  type: integer
                  title: Width
                  description: Width of the image
                  default: 0
                  minimum: 64
                height:
                  type: integer
                  title: Height
                  description: Height of the image
                  default: 0
                  minimum: 64
                safety_tolerance:
                  type: integer
                  title: Safety Tolerance
                  description: >-
                    Tolerance level for input and output moderation. Between 0
                    and 6, 0 being most strict, 6 being least strict.
                  minimum: 0
                  maximum: 5
                  default: 2
                  examples:
                    - 2
                output_format:
                  type: string
                  title: OutputFormat
                  description: The output format for the generated image.
                  default: jpeg
                  enum:
                    - jpeg
                    - png
                webhook_url:
                  type: string
                  title: Webhook Url
                  description: URL to receive webhook notifications
                  format: uri
                  minLength: 1
                  maxLength: 2083
                webhook_secret:
                  type: string
                  title: Webhook Secret
                  description: Optional secret for webhook signature verification
              required:
                - prompt
              x-apifox-orders:
                - prompt
                - input_image
                - input_image_2
                - input_image_3
                - input_image_4
                - input_image_5
                - input_image_6
                - input_image_7
                - input_image_8
                - seed
                - width
                - height
                - safety_tolerance
                - output_format
                - webhook_url
                - webhook_secret
            examples:
              '1':
                value:
                  prompt: ein fantastisches bild
                  width: 1024
                  height: 768
                  steps: 40
                  prompt_upsampling: false
                  seed: 42
                  guidance: 2.5
                  safety_tolerance: 2
                  interval: 2
                  output_format: jpeg
                summary: Text-to-image
              '2':
                value:
                  prompt: Change into blue clothes
                  input_image: >-
                    https://ts1.tc.mm.bing.net/th/id/OIP-C.5IV2b2rr3FWlGCAcA_1BmAHaLH?cb=ucfimg2&ucfimg=1&rs=1&pid=ImgDetMain&o=7&rm=3
                  seed: 42
                  width: 640
                  height: 640
                  safety_tolerance: 2
                  output_format: png
                  sync: true
                  enable_base64_output: false
                summary: Image editing
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                title: AsyncResponse
                type: object
                properties:
                  id:
                    type: string
                    title: Id
                  polling_url:
                    type: string
                    title: Polling Url
                  cost:
                    type: number
                    title: Cost
                    description: Cost in credits for this request
                  input_mp:
                    type: number
                    title: Input Mp
                    description: Input megapixels (2 decimal places)
                  output_mp:
                    type: number
                    title: Output Mp
                    description: Output megapixels (2 decimal places)
                required:
                  - id
                  - polling_url
                x-apifox-orders:
                  - id
                  - polling_url
                  - cost
                  - input_mp
                  - output_mp
          headers: {}
          x-apifox-name: OK
      security: []
      x-apifox-folder: Default module/Image Generation/Flux
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/5037766/apis/api-383499992-run
components:
  schemas: {}
  securitySchemes: {}
servers:
  - url: https://api.302.ai
    description: Production Environment
security: []

```

