
# Seedance-2.0 (视频生成)

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /volcengine/api/v3/contents/generations/tasks:
    post:
      summary: Seedance-2.0 (视频生成)
      deprecated: false
      description: >-
        Seedance 2.0 系列模型（包括 Seedance 2.0 和 Seedance 2.0 fast
        ）支持图像、视频、音频、文本等多种模态内容输入，具备视频生成、视频编辑、视频延长等能力，可高精度还原物品细节、音色、效果、风格、运镜等，保持稳定角色特征，赋予使用者如同导演般的掌控权。


        token 单价 × token 用量=按 token 单价 × (输入视频时长+输出视频时长) × 输出视频的宽 × 输出视频的高 ×
        输出视频的帧率/1024


        **价格**

        | 模型 | 输入类型 | 每1M token价格 |

        |------|---------|----------------|

        | doubao-seedance-2-0-260128（标准版） | 输入不含视频 | 7.884 PTC |

        | doubao-seedance-2-0-260128（标准版） | 输入包含视频 | 4.8 PTC|

        | doubao-seedance-2-0-fast-260128（快速版） | 输入不含视频 | 6.516 PTC|

        | doubao-seedance-2-0-fast-260128（快速版） | 输入包含视频 | 3.768 PTC|
      tags:
        - 视频生成/即梦
      parameters:
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
                model:
                  type: string
                  description: doubao-seedance-2-0-260128，doubao-seedance-2-0-fast-260128
                content:
                  type: array
                  items:
                    type: object
                    properties:
                      type:
                        type: string
                      text:
                        type: string
                      image_url:
                        type: object
                        properties:
                          url:
                            type: string
                        required:
                          - url
                        x-apifox-orders:
                          - url
                      role:
                        type: string
                      video_url:
                        type: object
                        properties:
                          url:
                            type: string
                        required:
                          - url
                        x-apifox-orders:
                          - url
                      audio_url:
                        type: object
                        properties:
                          url:
                            type: string
                        required:
                          - url
                        x-apifox-orders:
                          - url
                    required:
                      - type
                      - image_url
                      - role
                    x-apifox-orders:
                      - type
                      - text
                      - image_url
                      - role
                      - video_url
                      - audio_url
                  description: |-
                    输入给模型，生成视频的信息，支持文本、图片、音频、视频、样片任务 ID。支持以下几种组合：
                    文本
                    文本（可选）+ 图片
                    文本（可选）+ 视频
                    文本（可选）+ 图片 + 音频
                    文本（可选）+ 图片 + 视频
                    文本（可选）+ 视频 + 音频
                    文本（可选）+ 图片 + 视频 + 音频
                generate_audio:
                  type: boolean
                  description: >-
                    默认值 true

                    仅 Seedance 2.0 & 2.0 fast、Seedance 1.5 pro
                    支持控制生成的视频是否包含与画面同步的声音。

                    true：模型输出的视频包含同步音频。模型会基于文本提示词与视觉内容，自动生成与之匹配的人声、音效及背景音乐。建议将对话部分置于双引号内，以优化音频生成效果。例如：男人叫住女人说：“你记住，以后不可以用手指指月亮。”

                    false：模型输出的视频为无声视频。
                ratio:
                  type: string
                  description: >-
                    Seedance 2.0 & 2.0 fast、Seedance 1.5 pro 默认值为
                    adaptiveSeedance 1.0 lite 参考图场景默认值为 16:9其他模型：文生视频默认值
                    16:9，图生视频默认值 adaptive生成视频的宽高比例。不同宽高比对应的宽高像素值见下方表格。

                    16:9 

                    4:3

                    1:1

                    3:4

                    9:16

                    21:9

                    adaptive：根据输入自动选择最合适的宽高比（详见下文说明）

                    adaptive 适配规则

                    当配置 ratio 为 adaptive 时，模型会根据生成场景自动适配宽高比；实际生成的视频宽高比可通过
                    查询视频生成任务 API 返回的 ratio 字段获取。

                    支持模型：

                    Seedance 2.0 & 2.0 fast、Seedance 1.5 Pro 支持

                    其他模型仅图生视频场景支持，注意 Seedance 1.0 lite 参考图场景不支持。

                    取值规则：

                    文生视频：根据输入的提示词，智能选择最合适的宽高比。

                    首帧 / 首尾帧生视频：根据上传的首帧图片比例，自动选择最接近的宽高比。

                    多模态参考生视频：根据用户提示词意图判断，如果是首帧生视频/编辑视频/延长视频，以该图片/视频为准选择最接近的宽高比；否则，以传入的第一个媒体文件为准（优先级：视频＞图片）选择最接近的宽高比。
                duration:
                  type: integer
                  description: >-
                    默认值 5 

                    duration 和 frames 二选一即可，frames 的优先级高于
                    duration。如果您希望生成整数秒的视频，建议指定 duration。生成视频时长，仅支持整数，单位：秒。

                    Seedance 1.0 pro、Seedance 1.0 pro fast、Seedance 1.0 lite:
                    [2, 12] s。

                    Seedance 1.5 pro: [4,12] 或设置为-1

                    Seedance 2.0 & 2.0 fast:  [4,15] 或设置为-1

                    注意

                    Seedance 2.0 & 2.0 fast、Seedance 1.5 pro 支持两种配置方法

                    指定具体时长：支持有效范围内的任一整数。

                    智能指定：设置为 -1，表示由模型在有效范围内自主选择合适的视频长度（整数秒）。实际生成视频的时长可通过
                    查询视频生成任务 API 返回的 duration 字段获取。注意视频时长与计费相关，请谨慎设置。
                watermark:
                  type: boolean
                  description: |-
                    默认值 false 
                    生成视频是否包含水印。枚举值：
                    false：不含水印。
                    true：含有水印。
                callback_url:
                  type: string
                  description: >-
                    填写本次生成任务结果的回调通知地址。当视频生成任务有状态变化时，方舟将向此地址推送 POST 请求。

                    回调请求内容结构与查询任务API的返回体一致。

                    回调返回的 status 包括以下状态：

                    queued：排队中。

                    running：任务运行中。

                    succeeded： 任务成功。（如发送失败，即5秒内没有接收到成功发送的信息，回调三次）

                    failed：任务失败。（如发送失败，即5秒内没有接收到成功发送的信息，回调三次）

                    expired：任务超时，即任务处于运行中或排队中状态超过过期时间。可通过
                    execution_expires_after 字段设置过期时间
                return_last_frame:
                  type: boolean
                  description: >-
                    默认值 false

                    true：返回生成视频的尾帧图像。设置为 true 后，可通过 查询视频生成任务接口
                    获取视频的尾帧图像。尾帧图像的格式为 png，宽高像素值与生成的视频保持一致，无水印。

                    使用该参数可实现生成多个连续视频：以上一个生成视频的尾帧作为下一个视频任务的首帧，快速生成多个连续视频，调用示例详见
                    教程。

                    false：不返回生成视频的尾帧图像。
                service_tier:
                  type: string
                  description: >-
                    认值 default

                    不支持修改已提交任务的服务等级Seedance 2.0 & 2.0 fast
                    不支持离线推理指定处理本次请求的服务等级类型，枚举值：

                    default：在线推理模式，RPM 和并发数配额较低（详见 模型列表），适合对推理时效性要求较高的场景。

                    flex：离线推理模式，TPD 配额更高（详见 模型列表），价格为在线推理的 50%， 适合对推理时延要求不高的场景。
                execution_expires_after:
                  type: integer
                  description: >-
                    默认值 172800

                    任务超时阈值。指定任务提交后的过期时间（单位：秒），从 created at 时间戳开始计算。默认值 172800
                    秒，即 48 小时。取值范围：[3600，259200]。

                    不论使用哪种
                    service_tier，都建议根据业务场景设置合适的超时时间。超过该时间后任务会被自动终止，并标记为expired状态。
                draft:
                  type: string
                  description: >-
                    默认值 false

                    仅 Seedance 1.5 pro 支持控制是否开启样片模式。阅读文档 获取使用教程和注意事项。

                    true：开启样片模式，生成一段预览视频，快速验证场景结构、镜头调度、主体动作与 prompt 意图是否符合预期。消耗
                    token 数较正常视频更少，使用成本更低。

                    false：关闭样片模式，正常生成一段视频。

                    说明

                    开启样片模式后，将使用 480p 分辨率生成 Draft
                    视频（使用其他分辨率会报错），不支持返回尾帧功能，不支持离线推理功能。
                tools:
                  type: object
                  properties:
                    type:
                      type: string
                      description: >-
                        指定使用的工具类型。

                        web_search：联网搜索工具。阅读教程 获取详细代码示例。

                        说明

                        开启联网搜索后，模型会根据用户的提示词自主判断是否搜索互联网内容（如商品、天气等）。可提升生成视频的时效性，但也会增加一定的时延。

                        实际搜索次数可通过 查询视频生成任务 API 返回的 usage.tool_usage.web_search
                        字段获取，如果为 0 表示未搜索。
                  x-apifox-orders:
                    - type
                  description: 仅 Seedance 2.0 & 2.0 fast 支持
                  required:
                    - type
                safety_identifier:
                  type: string
                  description: >-
                    终端用户的唯一标识符，用于协助平台检测您的应用中可能违反火山方舟使用政策的用户。该标识符为英文字符串，需保证对单个用户固定且唯一，长度不超过
                    64 个字符。推荐传入对用户名、用户 ID 或邮箱进行哈希处理后生成的字符串，避免泄露用户隐私信息。
                resolution:
                  type: string
                  description: >-
                    Seedance 2.0 & 2.0 fast、Seedance 1.5 pro、Seedance 1.0 lite
                    默认值：720pSeedance 1.0 pro & pro-fast 默认值：1080p视频分辨率，枚举值：

                    480p

                    720p

                    1080p：Seedance 1.0 lite 参考图场景、Seedance 2.0 & 2.0 fast 不支持
                frames:
                  type: string
                  description: >-
                    Seedance 2.0 & 2.0 fast、Seedance 1.5 pro 暂不支持duration 和
                    frames 二选一即可，frames 的优先级高于 duration。如果您希望生成小数秒的视频，建议指定
                    frames。生成视频的帧数。通过指定帧数，可以灵活控制生成视频的长度，生成小数秒的视频。

                    由于 frames 的取值限制，仅能支持有限小数秒，您需要根据公式推算最接近的帧数。

                    计算公式：帧数 = 时长 × 帧率（24）。

                    取值范围：支持 [29, 289] 区间内所有满足 25 + 4n 格式的整数值，其中 n 为正整数。

                    例如：假设需要生成 2.4 秒的视频，帧数=2.4×24=57.6。由于 frames 不支持
                    57.6，此时您只能选择一个最接近的值。根据 25+4n 计算出最接近的帧数为 57，实际生成的视频为
                    57/24=2.375 秒。
                seed:
                  type: integer
                  description: >-
                    默认值 -1 

                    种子整数，用于控制生成内容的随机性。

                    取值范围：[-1, 2^32-1]之间的整数。

                    注意

                    相同的请求下，模型收到不同的seed值，如：不指定seed值或令seed取值为-1（会使用随机数替代）、或手动变更seed值，将生成不同的结果。

                    相同的请求下，模型收到相同的seed值，会生成类似的结果，但不保证完全一致。
                camera_fixed:
                  type: boolean
                  description: |-
                    默认值 false 
                    参考图场景不支持，Seedance 2.0 & 2.0 fast 暂不支持是否固定摄像头。枚举值：
                    true：固定摄像头。平台会在用户提示词中追加固定摄像头，实际效果不保证。
                    false：不固定摄像头。
              required:
                - model
                - content
              x-apifox-orders:
                - model
                - content
                - generate_audio
                - ratio
                - duration
                - watermark
                - callback_url
                - return_last_frame
                - service_tier
                - execution_expires_after
                - draft
                - tools
                - safety_identifier
                - resolution
                - frames
                - seed
                - camera_fixed
            examples:
              '1':
                value:
                  model: doubao-seedance-2-0-260128
                  content:
                    - type: text
                      text: >-
                        全程使用视频1的第一视角构图，全程使用音频1作为背景音乐。第一人称视角果茶宣传广告，seedance牌「苹苹安安」苹果果茶限定款；首帧为图片1，你的手摘下一颗带晨露的阿克苏红苹果，轻脆的苹果碰撞声；2-4
                        秒：快速切镜，你的手将苹果块投入雪克杯，加入冰块与茶底，用力摇晃，冰块碰撞声与摇晃声卡点轻快鼓点，背景音：「鲜切现摇」；4-6
                        秒：第一人称成品特写，分层果茶倒入透明杯，你的手轻挤奶盖在顶部铺展，在杯身贴上粉红包标，镜头拉近看奶盖与果茶的分层纹理；6-8
                        秒：第一人称手持举杯，你将图片2中的果茶举到镜头前（模拟递到观众面前的视角），杯身标签清晰可见，背景音「来一口鲜爽」，尾帧定格为图片2。背景声音统一为女生音色。
                    - type: image_url
                      image_url:
                        url: >-
                          https://ark-project.tos-cn-beijing.volces.com/doc_image/r2v_tea_pic1.jpg
                      role: reference_image
                    - type: image_url
                      image_url:
                        url: >-
                          https://ark-project.tos-cn-beijing.volces.com/doc_image/r2v_tea_pic2.jpg
                      role: reference_image
                    - type: video_url
                      video_url:
                        url: >-
                          https://ark-project.tos-cn-beijing.volces.com/doc_video/r2v_tea_video1.mp4
                      role: reference_video
                    - type: audio_url
                      audio_url:
                        url: >-
                          https://ark-project.tos-cn-beijing.volces.com/doc_audio/r2v_tea_audio1.mp3
                      role: reference_audio
                  generate_audio: true
                  ratio: '16:9'
                  duration: 11
                  watermark: false
                summary: seedance 2.0-多模态参考
              '2':
                value:
                  model: doubao-seedance-1-5-pro-251215
                  content:
                    - type: text
                      text: 女孩抱着狐狸，女孩睁开眼，温柔地看向镜头，狐狸友善地抱着，镜头缓缓拉出，女孩的头发被风吹动，可以听到风声
                    - type: image_url
                      image_url:
                        url: >-
                          https://ark-project.tos-cn-beijing.volces.com/doc_image/i2v_foxrgirl.png
                  generate_audio: true
                  ratio: adaptive
                  duration: 5
                  watermark: false
                summary: 有声视频-首帧
              '3':
                value:
                  model: doubao-seedance-1-5-pro-251215
                  content:
                    - type: text
                      text: 女孩抱着狐狸，女孩睁开眼，温柔地看向镜头，狐狸友善地抱着，镜头缓缓拉出，女孩的头发被风吹动，可以听到风声
                    - type: image_url
                      image_url:
                        url: >-
                          https://ark-project.tos-cn-beijing.volces.com/doc_image/i2v_foxrgirl.png
                  generate_audio: true
                  ratio: adaptive
                  duration: 5
                  watermark: false
                summary: 有声视频-首尾帧
              '4':
                value:
                  model: doubao-seedance-1-0-lite-i2v-250428
                  content:
                    - type: text
                      text: '[图1]戴着眼镜穿着蓝色T恤的男生和[图2]的柯基小狗，坐在[图3]的草坪上，3D卡通风格'
                    - type: image_url
                      image_url:
                        url: >-
                          https://ark-project.tos-cn-beijing.volces.com/doc_image/seelite_ref_1.png
                      role: reference_image
                    - type: image_url
                      image_url:
                        url: >-
                          https://ark-project.tos-cn-beijing.volces.com/doc_image/seelite_ref_2.png
                      role: reference_image
                    - type: image_url
                      image_url:
                        url: >-
                          https://ark-project.tos-cn-beijing.volces.com/doc_image/seelite_ref_3.png
                      role: reference_image
                  ratio: '16:9'
                  duration: 5
                  watermark: false
                summary: seedance-lite-参考图
              '5':
                value:
                  model: doubao-seedance-1-0-lite-i2v-250428
                  content:
                    - type: text
                      text: 女孩抱着狐狸，女孩睁开眼，温柔地看向镜头，狐狸友善地抱着，镜头缓缓拉出，女孩的头发被风吹动
                    - type: image_url
                      image_url:
                        url: data:image/png;base64,aHR0******cG5n
                  ratio: adaptive
                  duration: 5
                  watermark: false
                summary: 图生视频-base64编码
              '6':
                value:
                  model: doubao-seedance-1-0-pro-250528
                  content:
                    - type: text
                      text: >-
                        写实风格，晴朗的蓝天之下，一大片白色的雏菊花田，镜头逐渐拉近，最终定格在一朵雏菊花的特写上，花瓣上有几颗晶莹的露珠
                  ratio: '16:9'
                  duration: 5
                  watermark: false
                summary: 文生视频
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                required:
                  - id
                x-apifox-orders:
                  - id
              example:
                id: cgt-20260403112523-rt66c
          headers: {}
          x-apifox-name: 成功
      security: []
      x-apifox-folder: 视频生成/即梦
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/4012774/apis/api-437932283-run
components:
  schemas: {}
  securitySchemes:
    apiKeyAuth:
      type: apikey
      in: header
      name: Authorization
    BearerAuth:
      type: jwt
      scheme: bearer
      bearerFormat: JWT
      description: 使用火山方舟 API Key 进行认证
servers:
  - url: https://api.302.ai
    description: 海外环境
  - url: https://api.302ai.cn
    description: 国内环境1
  - url: https://api.302ai.com
    description: 国内环境2
security: []

```