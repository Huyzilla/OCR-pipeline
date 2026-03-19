# Public_032

# Dòng điện một chiều (Direct Current – DC)

## Định nghĩa (Definition)

Dòng điện một chiều (DC) là dòng điện mà các electron chảy liên tục theo **một hướng** trong mạch kín. Loại điện áp tạo ra dòng điện này gọi là **điện áp một chiều (DC voltage)** , và dòng điện gọi là **dòng điện một chiều (DC current)**.

**Các nguồn DC điển hình:** Pin, ắc quy, máy phát DC.

## Định luật Ohm (Ohm’s Law)

Có một mối quan hệ xác định giữa ba đặc tính điện cơ bản: **dòng điện (I), điện áp (V), điện trở (R)**.

Định luật Ohm do nhà vật lý người Đức **Georg Simon Ohm** phát hiện vào thế kỷ 19:

I=VRI = V/R

Trong đó:

  * II: dòng điện (amps – A)

  * VV: điện áp (volts – V)

  * RR: điện trở (ohms – Ω)


**Giải thích:**

  * Điện áp 1 V đặt vào điện trở 1 Ω → dòng điện 1 A chảy qua.

  * Điện trở tăng → dòng điện giảm (với cùng điện áp).


**Thiết bị Ohmic và Non-Ohmic:**

  * **Ohmic:** Tuân theo luật Ohm (điện trở tuyến tính, ví dụ dây dẫn, điện trở thông thường).

  * **Non-Ohmic:** Không tuân theo (ví dụ transistor, diode).


## Ví dụ minh họa

**Ví dụ 1:** Biết V=12 VV = 12V , R=6 ΩR = 6Ω. Tìm dòng điện II:

I=VR= 2A

**Ví dụ thực tế:** Pin 4.2 V cấp cho tải 0.5 Ω:

I= 8.4A

Nếu pin còn 3.7 V, dòng điện giảm:

I= 7.4A

**Ví dụ 2:** Biết V=24 VV = 24\,V, I=6 AI = 6\,A. Tìm điện trở RR:

$$
R=VI=246=4ΩR=V/I=24/6=4ΩR = VI = 246 = 4,Omega R  =  V/I  =  24/6  =  4Omega
$$

**Ví dụ 3:** Biết I=5 AI = 5\,A, R=8 ΩR = 8\,Ω. Tìm điện áp VV:

## Công suất điện (Power Calculation)

Công suất (P) do dòng điện tạo ra trong điện trở tính theo:

$$
P=V⋅I=V2R=I2⋅RP=V⋅I=V2R=I2⋅RP = V cdot I = V2R = I2 cdot RP  =  V  cdot I  = frac{V^{2}}{R} =  I^{2} cdot R
$$

**Ví dụ:** Pin 4.2 V, điện trở 0.5 Ω, dòng điện 8.4 A:

P=4.2×8.4=35.3 WP = 4.2 \times 8.4 = 35.3\,W

Như vậy, cuộn dây 0.5 Ω với pin sạc đầy 4.2 V sẽ kéo 8.4 A và cung cấp 35.3 W. Khi điện trở tăng → dòng điện giảm → công suất giảm.

# Dòng điện xoay chiều (Alternating Current – AC)

## Định nghĩa (Definition)

Dòng điện xoay chiều (AC) là dòng điện mà các electron **thay đổi hướng liên tục** theo thời gian. Điện áp AC buộc electron chảy theo một hướng, sau đó theo hướng ngược lại, tuần hoàn liên tục.

**Nguồn AC:** Máy phát điện.  
**Ứng dụng:** Cung cấp điện cho hộ gia đình, nhà máy, văn phòng.

## Dạng sóng (Waveform)

AC có nhiều dạng sóng khác nhau. Khi kết nối nguồn AC với dao động kế và vẽ điện áp theo thời gian, các dạng sóng phổ biến:

  * **Sóng sin:** Dạng sóng chính dùng trong dân dụng và công nghiệp.

  * **Sóng vuông và sóng tam giác:** Thường dùng trong mạch điện tử và điều khiển.


## Mô tả toán học của sóng sin AC

Sóng sin AC có thể mô tả bằng hàm toán học:

$$
V(t)=Vpsin(2πft+ϕ)V(t)=Vp∖sin(2πft+ϕ)V(t) = Vpsin(2pi ft + phi)V(t) =  V_{p}backslash sin(2pi f t  +  phi)
$$

Trong đó:

  * V(t)V(t): điện áp theo thời gian (V)

  * VpV_p: biên độ (amplitude), điện áp cực đại ±Vp

  * sin(): dao động hình sin tuần hoàn

  * 2π2\pi: hằng số chuyển đổi từ chu kỳ (Hz) sang tần số góc (rad/s)

  * ff: tần số (Hz), số dao động trong 1 giây

  * tt: thời gian (s)

  * ϕ\phi: pha (phase), dịch chuyển sóng theo thời gian, đơn vị độ (°)


**Ví dụ:** Ở Mỹ, điện áp AC cho hộ gia đình: biên độ 170 V, tần số 60 Hz, pha 0°:

$$
V(t)=170sin(2π⋅60⋅t)V(t)=170∖sin(2π⋅60⋅t)V(t) = 170sin(2pi cdot 60 cdot t)V(t) =  170 backslash sin(2 pi cdot 60  cdot t)
$$

## Ứng dụng (Applications)

Nguồn AC phổ biến trong **nhà dân, cửa hàng, văn phòng** , vì:

  1. **Truyền tải dễ dàng trên khoảng cách dài:**

* Điện áp cao (>110 kV) → dòng điện thấp → giảm tổn hao năng lượng (I²R) trên đường dây.

* AC có thể biến đổi điện áp bằng **máy biến áp** , tiện lợi cho truyền tải.

  2. **Cung cấp năng lượng cho động cơ điện:**

* Động cơ AC chuyển năng lượng điện thành cơ học.

* Máy phát điện cũng là động cơ hoạt động ngược lại (quay trục sinh điện áp).

* Thiết bị sử dụng AC: máy rửa chén, tủ lạnh, máy lạnh, máy giặt, máy bơm,…


## Điện áp hiệu dụng (RMS Voltage)

Để tính công suất thực tế của AC, sử dụng **điện áp RMS (Root Mean Square)** :

VRMS=Vp2V_\text{RMS} = \frac{V_p}{\sqrt{2}}

Trong đó VpV_p là biên độ cực đại.

Ví dụ: Nguồn AC 170 V (biên độ) → điện áp RMS:

VRMS=1702≈120 VV_\text{RMS} = \frac{170}{\sqrt{2}} \approx 120\,V

Điện áp RMS cho biết mức điện áp tương đương DC tạo ra cùng công suất trên tải điện trở.

## Công suất AC (AC Power)

**Công suất tức thời:**

P(t)=V(t)⋅I(t)P(t) = V(t) \cdot I(t)

**Lưu ý:** Đối với tải thuần trở, ϕ=0\phi = 0, công suất trung bình:

Pavg=VRMS⋅IRMSP_\text{avg} = V_\text{RMS} \cdot I_\text{RMS}

## So sánh DC và AC


| Tiêu chí | DC | AC |
| --- | --- | --- |
| Dòng chảy điện | Một hướng | Thay đổi luân phiên |
| Nguồn | Pin, ắc quy, máy phát DC | Máy phát AC, lưới điện |
| Truyền tải | Khó trên khoảng cách dài | Dễ dàng qua máy biến áp |
| Ứng dụng chính | Điện tử, thiết bị nhỏ | Nhà dân, công nghiệp, động cơ |