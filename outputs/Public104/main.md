# Public_104

## **1. Khái niệm cơ bản về Hidden Markov Model (HMM)**

Hidden Markov Model (HMM) là một mô hình thống kê được sử dụng để phân tích các chuỗi dữ liệu có tính chất tuần tự, trong đó trạng thái thực của hệ thống (trạng thái ẩn) không thể quan sát trực tiếp, nhưng có thể suy ra thông qua các quan sát (observations). HMM kết hợp hai quá trình ngẫu nhiên:

- Một quá trình Markov ẩn, mô tả sự chuyển đổi giữa các trạng thái ẩn.
- Một quá trình phát xạ, liên kết mỗi trạng thái ẩn với một tập các quan sát theo một phân phối xác suất.

HMM thường được biểu diễn thông qua các thành phần sau:

- **Tập trạng thái ẩn (Hidden States):** Đại diện cho các trạng thái không quan sát được của hệ thống.
- **Ma trận xác suất chuyển trạng thái (State Transition Matrix):** Xác định xác suất chuyển từ một trạng thái ẩn này sang trạng thái ẩn khác.
- **Ma trận xác suất phát xạ (Emission Probability Matrix):** Mô tả xác suất của một quan sát cụ thể dựa trên trạng thái hiện tại.
- **Phân phối xác suất ban đầu (Initial State Distribution):** Xác định trạng thái khởi đầu của hệ thống.

#### **2. Sự khác biệt giữa Markov Chain và HMM**

Markov Chain là một mô hình toán học đơn giản hơn HMM, trong đó:

- Trạng thái của Markov Chain là có thể quan sát trực tiếp.
- Xác suất chuyển trạng thái chỉ phụ thuộc vào trạng thái hiện tại, không quan tâm đến các trạng thái trước đó.

Ngược lại, HMM phức tạp hơn:

- Trạng thái ẩn của HMM không thể quan sát trực tiếp, mà chỉ có thể suy đoán thông qua các quan sát.
- HMM bổ sung thêm quá trình phát xạ, liên kết các trạng thái ẩn với dữ liệu quan sát.

Ví dụ minh họa: Trong Markov Chain, nếu ta đang xem một chuỗi các điều kiện thời tiết (nắng, mưa), bạn có thể quan sát trực tiếp điều kiện thời tiết tại từng thời điểm. Trong HMM, các điều kiện thời tiết có thể được ẩn (không trực tiếp

quan sát được), nhưng ta có thể suy luận từ các quan sát như mức độ ẩm, nhiệt độ, hoặc áp suất không khí.

# **2.1. Vai trò và ứng dụng của HMM trong các bài toán thực tiễn**

HMM đóng vai trò quan trọng trong nhiều lĩnh vực nghiên cứu và ứng dụng, đặc biệt là trong xử lý chuỗi dữ liệu. Một số ứng dụng điển hình của HMM bao gồm:

### **2.1.1. Xử lý ngôn ngữ tự nhiên (Natural Language Processing - NLP):**

- o Gắn thẻ từ loại (POS Tagging): Dự đoán nhãn ngữ pháp (danh từ, động từ,...) của các từ trong câu.
- o Nhận dạng thực thể (Named Entity Recognition): Xác định tên riêng, địa danh, hoặc tổ chức trong văn bản.

## **2.1.2. Nhận dạng giọng nói (Speech Recognition):**

o Mô hình hóa các chuỗi âm thanh để chuyển đổi thành văn bản.

## **2.1.3. Phân tích sinh học (Bioinformatics):**

- o Dự đoán cấu trúc protein từ chuỗi axit amin.
- o Phân tích trình tự DNA để xác định gen.

## **2.1.4. Phát hiện bất thường (Anomaly Detection):**

- o Dự đoán lỗi trong hệ thống máy tính hoặc mạng lưới.
- o Phát hiện gian lận trong các giao dịch tài chính.

# **2.1.5. Ứng dụng trong thời gian thực:**

- o Phân tích dữ liệu cảm biến trong hệ thống IoT (Internet of Things).
- o Dự đoán trạng thái hoạt động trong các hệ thống điều khiển tự động.

Nhờ khả năng kết hợp tính xác suất và dự đoán trạng thái, HMM trở thành một công cụ mạnh mẽ trong việc mô hình hóa các quá trình phức tạp mà các trạng thái ẩn không thể quan sát trực tiếp.

## **2.2. Cấu trúc cơ bản của Hidden Markov Model**

2.2.1. Mô hình Markov và trạng thái ẩn

Hidden Markov Model (HMM) là sự mở rộng của mô hình Markov truyền thống, trong đó trạng thái của hệ thống không thể quan sát trực tiếp, mà chỉ có thể được suy luận từ các quan sát (emissions). Một hệ thống được mô tả bởi HMM có các trạng thái ẩn liên kết với một tập hợp các quan sát cụ thể thông qua xác suất phát xạ.

Trong HMM, hai quá trình ngẫu nhiên được kết hợp:

- **Quá trình Markov ẩn:** Mô tả sư chuyển đổi giữa các trang thái ẩn theo xác suất.
- Quá trình phát xa: Liên kết mỗi trạng thái ẩn với các quan sát thông qua phân phối xác suất phát xạ.

HMM thường được biểu diễn dưới dạng một đồ thị có hướng, trong đó các nút là trạng thái và các cạnh thể hiện xác suất chuyển đổi giữa các trạng thái.

2.2.2. Các thành phần chính của HMM

Một HMM được định nghĩa bởi bốn thành phần chính:

2.2.3. Tập trạng thái (Hidden States)

Tập trạng thái ẩn của HMM được ký hiệu là  $S=\{S_1,S_2,...,S_N\}$ , trong đó:

- S<sub>i</sub>: Trang thái ẩn thứ iii.
- N: Số lương trang thái ẩn.

Tại mỗi thời điểm, hệ thống sẽ nằm ở một trong các trạng thái S<sub>i</sub>, nhưng trạng thái này không thể quan sát trực tiếp mà chỉ có thể suy ra từ các quan sát.

Ví dụ: Trong bài toán nhận dạng giọng nói, các trạng thái ẩn có thể là các âm vị (phonemes) mà người nói đang phát âm.

2.2.4. Ma trận chuyển trạng thái (State Transition Matrix)

Ma trận chuyển trạng thái, ký hiệu là  $A=[a_{ij}]$ , là một ma trận vuông kích thước 2025-09-28 17.44.01\_A N×N, trong đó:

- $a_{ij}=P(S_i|S_i)$ : Xác suất chuyển từ trang thái  $S_i$  sang trang thái  $S_i$ .
- $\sum_{j=1}^{N} a_{ij} = 1$ : Tổng các xác suất từ một trạng thái phải bằng 1.

Ma trận A biểu diễn các mối quan hệ giữa các trạng thái ẩn trong mô hình.

Ví dụ: Trong một chuỗi thời tiết, xác suất chuyển từ trạng thái "nắng" sang "mưa" là một phần của ma trận chuyển trạng thái.

2.2.5. Ma trận xác suất phát xạ (Emission Probability Matrix)

Ma trận xác suất phát xạ, ký hiệu là  $B=[b_j(k)]$ , là một ma trận kích thước  $N\times M$ , trong đó:

- $b_i(k) = P(O_k \mid S_i)$ : Xác suất quan sát  $O_k$  xảy ra khi hệ thống ở trạng thái  $S_i$ .
- O ={O<sub>1</sub>,O<sub>2</sub>,...,O<sub>M</sub>}: Tập các quan sát có thể xảy ra, với M là số lượng quan sát.

Ma trận B mô tả mối quan hệ giữa trạng thái ẩn và quan sát.

Ví dụ: Trong bài toán nhận dạng giọng nói, các quan sát có thể là các đặc trưng âm thanh (spectral features) được trích xuất từ tín hiệu âm thanh.

2.2.6. Phân phối xác suất ban đầu (Initial State Distribution)

Phân phối xác suất ban đầu, ký hiệu là  $\pi = {\pi_1, \pi_2, ..., \pi_N}$ , trong đó:

- $\pi_i = P(S_i)$ : Xác suất hệ thống bắt đầu ở trạng thái  $S_i$ .
- $\sum_{i=1}^{N} \pi_i = 1$ : Tổng xác suất của tất cả các trạng thái ban đầu phải bằng 1.

Phân phối  $\pi$  cung cấp thông tin về trạng thái khởi đầu của hệ thống trước khi các quan sát được thực hiện.

### 2.3. Công thức tổng quát của HMM

Một HMM được định nghĩa bởi các tham số  $\lambda$ =(A,B, $\pi$ ), trong đó:

- $A = [a_{ii}]$ : Ma trận chuyển trạng thái.
- $B = [b_j(k)]$ : Ma trận xác suất phát xạ.
- $\pi = {\pi_i}$ : Phân phối xác suất ban đầu.

Cho một chuỗi quan sát  $O=\{O_1,O_2,...,O_T\}$  với chiều dài T, xác suất của chuỗi quan sát được tính theo công thức:

$$P(O \mid \lambda) = \sum_{Q} P(O, Q \mid \lambda) = \sum_{Q} P(Q \mid \lambda) \cdot P(O \mid Q, \lambda)$$

Trong đó:

- Q = {Sq1,Sq2,…,SqT}: Một chuỗi trạng thái ẩn.
- Tổng Σ<sup>Q</sup> được tính trên tất cả các chuỗi trạng thái có thể xảy ra.

Công thức này cho phép ta tính xác suất quan sát của một chuỗi và xác định chuỗi trạng thái ẩn tối ưu.

#### **3. Ba bài toán cơ bản của Hidden Markov Model (HMM)**

Hidden Markov Model (HMM) được sử dụng để giải quyết ba bài toán cơ bản trong các ứng dụng thực tế. Các bài toán này là trung tâm của việc áp dụng HMM vào việc phân tích dữ liệu tuần tự. Dưới đây là chi tiết từng bài toán.

## 3.1.Bài toán 1: Đánh giá (Evaluation)

#### **Mục tiêu:**

Tính xác suất của một chuỗi quan sát O={O1,O2,…,OT} đã cho, dựa trên mô hình HMM λ=(A,B,π).

# **Ý nghĩa:**

Bài toán này giúp đánh giá mức độ phù hợp của một chuỗi quan sát với một mô hình HMM cụ thể. Đây là bước cần thiết để so sánh và lựa chọn mô hình tốt nhất từ các mô hình cạnh tranh.

#### **Công thức:**

Xác suất của chuỗi quan sát P(O ∣ λ) được tính bằng cách tổng hợp xác suất trên tất cả các chuỗi trạng thái ẩn Q={q1,q2,…,qT}:

$$P(O \mid \lambda) = \sum_{Q} P(P, Q \mid \lambda)$$

# **Thách thức:**

Việc tính toán trực tiếp rất phức tạp, vì số lượng các chuỗi trạng thái Q tăng theo hàm mũ với chiều dài T của chuỗi quan sát.

#### **Giải pháp:**

Sử dụng thuật toán **Forward**:

- Thuật toán này tính toán xác suất một cách hiệu quả bằng cách sử dụng phương pháp đệ quy.
- Độ phức tạp được giảm từ O(N<sup>T</sup> ) xuống O(N<sup>2</sup>T), trong đó N là số trạng thái ẩn.

### 3.2. Bài toán 2: Giải mã (Decoding)

## **Mục tiêu:**

Tìm chuỗi trạng thái ẩn tối ưu Q∗={q<sup>1</sup> ∗ ,q<sup>2</sup> ∗ ,…,q<sup>T</sup> <sup>∗</sup>} tương ứng với chuỗi quan sát O, sao cho:

$$Q^* = arg \max_{Q} P(Q \mid O, \lambda)$$

# **Ý nghĩa:**

Bài toán này giúp xác định chuỗi trạng thái ẩn khả dĩ nhất, giải thích tốt nhất cho chuỗi quan sát. Đây là một bước quan trọng trong các ứng dụng như nhận dạng giọng nói và phân tích chuỗi sinh học.

#### **Thách thức:**

Việc tìm kiếm chuỗi trạng thái tối ưu yêu cầu tối ưu hóa toàn cục trên toàn bộ chuỗi thời gian.

### **Giải pháp:**

Sử dụng thuật toán **Viterbi**:

- Thuật toán này dựa trên lập trình động, tìm chuỗi trạng thái tối ưu bằng cách lưu trữ các giá trị tối đa tại mỗi bước.
- Độ phức tạp của thuật toán là O(N<sup>2</sup>T).
- 3.3. Bài toán 3: Học (Learning)

#### **Mục tiêu:**

Ước lượng các tham số của mô hình λ=(A,B,π) từ một tập dữ liệu quan sát O={O(1),O(2),…,O(K)}.

## **Ý nghĩa:**

Bài toán này giúp xây dựng một mô hình HMM phù hợp từ dữ liệu quan sát, phục vụ cho việc phân tích và dự đoán.

### **Thách thức:**

Không thể tối ưu trực tiếp P(O∣λ) vì các trạng thái ẩn không được quan sát trực tiếp.

#### **Giải pháp:**

Sử dụng thuật toán **Baum-Welch** hoặc **Expectation-Maximization (EM)**:

- Thuật toán này lặp lại hai bước:
  - 1. **E-step (Expectation):** Tính xác suất kỳ vọng cho các trạng thái ẩn dựa trên các tham số hiện tại.
  - 2. **M-step (Maximization):** Cập nhật các tham số A,B,π để tối đa hóa xác suất quan sát P(O∣λ).
- Thuật toán hội tụ đến một cực đại cục của P(O∣λ).

![](images/image1.jpg)