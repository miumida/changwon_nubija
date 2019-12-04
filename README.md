# 창원 누비자 터미널 현황 Sensor
창원 누비자 터미널 현황 Home Assistant Sensor 입니다.<br>
터미널에 반납 가능 거치대와 대여 가능 자전거를 표시해 줍니다.<br>
![screenshot_l](https://github.com/miumida/changwon_nubija/blob/master/image/Screenshot_1.png?raw=true)<br>
![screenshot_2](https://github.com/miumida/changwon_nubija/blob/master/image/Screenshot_2.png?raw=true)<br>
<br><br>
## Installation
- HA 설치 경로 아래 custom_components 에 파일을 넣어줍니다.<br>
  `<config directory>/custom_components/changwon_nubija/__init__.py`<br>
  `<config directory>/custom_components/changwon_nubija/manifest.json`<br>
  `<config directory>/custom_components/changwon_nubija/sensor.py`<br>
- configuration.yaml 파일에 설정을 추가합니다.<br>
- Home-Assistant 를 재시작합니다<br>
<br><br>
## Usage
### configuration
- HA 설정에 창원 누비자 sensor를 추가합니다.<br>
```yaml
sensor:
  - platform: changwon_nubija
    terminal_index:
      - '0'
      - '10'
```
