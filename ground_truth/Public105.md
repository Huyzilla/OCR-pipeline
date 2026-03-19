# Public_105

# T **huật toán liên quan đến Hidden Markov Model (HMM)**

Các thuật toán liên quan đến HMM là trung tâm của việc áp dụng mô hình trong các bài toán thực tiễn. Dưới đây là ba thuật toán quan trọng, mỗi thuật toán giải quyết một trong ba bài toán cơ bản của HMM.

## **Thuật toán Forward và Backward**

### **Mục đích:**

Tính xác suất của một chuỗi quan sát O={O1,O2,…,OT} dựa trên một mô hình HMM λ=(A,B,π).

### **Thuật toán Forward**

Forward algorithm tính xác suất P(O ∣ λ) bằng cách sử dụng đệ quy.

  * **Biến forward** αt(i): Xác suất của chuỗi quan sát một phần O1,O2,…,Ot và hệ thống ở trạng thái Si tại thời điểm t:


$$
αt(i)=P(O1,O2,…Ot,qt=Si|λ)alpha_{t}(i) =  P(O_{1},O_{2},ldots O_{t},q_{t} = S_{i}|lambda)
$$

  * **Quy trình tính toán:**

1. **Khởi tạo:**


$$
αt(i)=πibi(O1),1≤i≤Nalpha_{t}(i) =  pi_{i}b_{i}left( O_{1} right), 1 leq  i  leq  N
$$

  2. **Đệ quy:**


$$
αt+1(j)=∑i=1Nαt(i)αijbj(Ot+1),1≤j≤N,1≤t≤T−1alpha_{t + 1}(j) = sum_{i = 1}^{N}{alpha_{t}(i)alpha_{ij}b_{j}(O_{t + 1})}, 1 leq j  leq N, 1 leq t  leq T - 1
$$

  3. **Kết thúc:**


$$
P(O|λ)=∑i=1NαT(i)P(O | lambda) =  sum_{i = 1}^{N}{alpha_{T}(i)}
$$

  * **Độ phức tạp:** O(N2T).


### **Thuật toán Backward**

Backward algorithm hỗ trợ tính toán tương tự nhưng từ cuối chuỗi quan sát trở về đầu.

  * **Biến backward** βt(i): Xác suất của chuỗi quan sát từ Ot+1,Ot+2,…,OT​, với trạng thái qt=Si tại thời điểm t:


βt(i) = P(Ot+1,Ot+2,…,OT∣qt = Si,λ)

  * **Quy trình tính toán:**

1. **Khởi tạo:**


βT(i) = 1, 1 ≤ i ≤ N

  2. **Đệ quy:**


$$
βt(i)=∑j=1Naijbj(Ot+1)βt+1(j),1≤t≤T−1beta_{t}(i) =  sum_{j = 1}^{N}{a_{ij}b_{j}left( O_{t + 1} right)beta_{t + 1}(j), 1  leq t  leq T - 1}
$$

  3. **Kết thúc:** Tính xác suất tổng quát:


$$
P(O|λ)=∑i=1Nπibi(O1)β1(i)P(O | lambda) =  sum_{i = 1}^{N}{pi_{i}b_{i}left( O_{1} right)beta_{1}(i)}
$$

  * **Độ phức tạp:** O(N2T).


## **Thuật toán Viterbi**

### **Mục đích:**

Tìm chuỗi trạng thái ẩn tối ưu Q∗={q1∗,q2∗,…,qT∗} giải thích tốt nhất chuỗi quan sát O.

### **Quy trình tính toán:**

  * **Biến trạng thái** δt(i): Xác suất lớn nhất của chuỗi trạng thái dẫn đến Si​ tại thời điểm t:


$$
δt(i)=maxq1,q2,…,qt−1P(q1,q2,…,qt=Si,O1,O2,…,Ot|λ)delta_{t}(i) =  max_{q_{1},q_{2},ldots,q_{t - 1}}{Pleft( q_{1},q_{2},ldots,q_{t} =  S_{i}, O_{1},O_{2},ldots, O_{t }| lambda right)}
$$

  * **Bước thực hiện:**

1. **Khởi tạo:**


δ1(i) = πibi(O1) , 1 ≤ i ≤ N
$ψ1(j)=0,1≤i≤Npsi_{1}(j) = 0,  1  leq  i  leq  N$

  2. **Đệ quy:**


$$
δt+1(j)=Nmaxi=1δt(i)aijbj(Ot+1),1≤j≤N,1≤t≤T−1delta_{t + 1}(j) =  begin{array}{r}
N 
max 
i = 1
end{array}{delta_{t}(i)a_{ij}b_{j}left( O_{t + 1} right),  1 leq j leq N, 1 leq t leq T - 1}
$$
$$
ψt+1(j)=argNmaxi=1δt(i)aij,1≤j≤Npsi_{t + 1}(j) = arg{begin{array}{r}
N 
max 
i = 1
end{array}delta_{t}(i)a_{ij}  , }1 leq j leq N
$$

  3. **Kết thúc:**


$$
P(Q*,O|λ)=Nmaxi=1δT(i)Pleft( Q^{*}, O  right| lambda) =  begin{array}{r}
N 
max 
i = 1
end{array}{delta_{T}(i)}
$$
$$
qT*=argNmaxi=1δT(i)q_{T}^{*} = argbegin{array}{r}
N 
max 
i = 1
end{array}{delta_{T}(i)}
$$

  4. **Truy vết trạng thái tối ưu:**


$$
qt*=ψt+1(qt+1*),t=T−1,T−2,…,1q_{t}^{*} = psi_{t + 1}left( q_{t + 1}^{*} right), t = T - 1, T - 2, ldots, 1
$$

  * **Độ phức tạp:** O(N2T).


# **Các giả định của Hidden Markov Model (HMM)**

Hidden Markov Model (HMM) dựa trên hai giả định cơ bản, giúp đơn giản hóa việc mô hình hóa và tính toán xác suất trong các bài toán thực tế. Mặc dù những giả định này có thể không hoàn toàn chính xác trong mọi trường hợp, chúng vẫn đủ mạnh để mô tả nhiều hệ thống thực tế một cách hiệu quả.

## **Giả định Markov (Markov Assumption)**

### **Định nghĩa:**

Giả định Markov phát biểu rằng trạng thái hiện tại qtq_tqt​ chỉ phụ thuộc vào trạng thái ngay trước đó qt−1​, không phụ thuộc vào các trạng thái trước đó trong chuỗi.

P(qt∣qt−1,qt−2,…,q1) = P(qt ∣ qt−1)

### **Ý nghĩa:**

  * Giả định này giảm độ phức tạp của mô hình, chỉ yêu cầu xét mối quan hệ giữa hai trạng thái liên tiếp thay vì toàn bộ chuỗi trạng thái.

  * Trong thực tế, giả định Markov có thể hiểu là một hệ thống "có trí nhớ ngắn hạn", nơi trạng thái hiện tại chứa đủ thông tin để dự đoán trạng thái tiếp theo.


### **Hạn chế:**

  * Hệ thống thực tế có thể bị ảnh hưởng bởi nhiều trạng thái trong quá khứ, không chỉ bởi trạng thái ngay trước đó. Tuy nhiên, việc tăng bậc của mô hình Markov (Markov bậc cao hơn) có thể giúp giảm bớt hạn chế này, nhưng làm tăng độ phức tạp tính toán.


## **Giả định độc lập quan sát (Independence Assumption)**

### **Định nghĩa:**

Giả định này cho rằng mỗi quan sát OtO_tOt​ tại thời điểm ttt chỉ phụ thuộc vào trạng thái hiện tại qtq_tqt​, không phụ thuộc vào các quan sát khác hoặc các trạng thái khác trong chuỗi.

P(Ot ∣ qt,qt−1,Ot−1,… ) = P(Ot ∣ qt)

### **Ý nghĩa:**

  * Giả định này cho phép ta mô hình hóa mối quan hệ giữa trạng thái ẩn và quan sát một cách độc lập, giảm đáng kể độ phức tạp khi tính toán xác suất.

  * Đây là một trong những lý do HMM được áp dụng rộng rãi trong các bài toán như nhận dạng giọng nói và gắn thẻ từ loại.


### **Hạn chế:**

  * Trong thực tế, các quan sát thường có mối liên hệ phụ thuộc với nhau, đặc biệt trong các chuỗi dữ liệu có tính chất tuần tự cao. Giả định này có thể không hoàn toàn chính xác, nhưng thường được chấp nhận để đơn giản hóa mô hình.


Hai giả định Markov và độc lập quan sát là nền tảng của Hidden Markov Model, giúp mô hình này trở thành một công cụ đơn giản nhưng mạnh mẽ để mô tả các chuỗi dữ liệu tuần tự. Mặc dù có những hạn chế nhất định, chúng cho phép HMM áp dụng hiệu quả trong các bài toán thực tế với độ phức tạp tính toán thấp.

# **Ứng dụng của Hidden Markov Model (HMM) vào Gắn thẻ từ loại (POS Tagging)**

Gắn thẻ từ loại (Part-of-Speech Tagging - POS Tagging) là một bài toán quan trọng trong xử lý ngôn ngữ tự nhiên (NLP), nhằm gán nhãn ngữ pháp (danh từ, động từ, tính từ,...) cho từng từ trong câu. Hidden Markov Model (HMM) là một phương pháp phổ biến để giải quyết bài toán này nhờ khả năng mô hình hóa chuỗi trạng thái ẩn (các nhãn từ loại) dựa trên chuỗi quan sát (các từ trong câu).

## **Mô hình HMM cho POS Tagging**

Để áp dụng HMM vào bài toán POS Tagging, chúng ta cần xác định các thành phần của mô hình:

  * **Tập trạng thái ẩn (S):**

* Là tập các nhãn từ loại (POS tags), ví dụ:  
S={NN (danh từ),VB (động từ),JJ (tính từ),… }.

  * **Tập quan sát (O):**

* Là tập các từ trong câu, ví dụ: O={The, cat, runs, fast}

  * **Phân phối xác suất ban đầu (π):**

* Xác suất một từ trong câu bắt đầu với một từ loại cụ thể: πi=P(S1=i)  
Ví dụ: Một câu thường bắt đầu bằng các nhãn như DT (mạo từ) hoặc NN (danh từ).

  * **Ma trận chuyển trạng thái (A):**

* Xác suất chuyển từ nhãn từ loại này sang nhãn từ loại khác: aij=P(St+1=j∣St=i)  
Ví dụ: Sau một danh từ (NN), khả năng cao sẽ là một động từ (VB) hoặc mạo từ (DT).

  * **Ma trận xác suất phát xạ (B):**

* Xác suất một nhãn từ loại phát sinh một từ cụ thể: bj(Ot)=P(Ot∣St=j)  
Ví dụ: Xác suất từ "runs" thuộc nhãn động từ (VB) sẽ cao hơn các nhãn khác.


## **Thuật toán Viterbi để giải bài toán POS Tagging**

POS Tagging sử dụng thuật toán Viterbi để tìm chuỗi nhãn từ loại tối ưu S∗={S1∗,S2∗,…,ST∗} tương ứng với chuỗi quan sát O={O1,O2,…,OT}.

### **Quy trình thực hiện:**

**B1: Khởi tạo:** Tại thời điểm t=1:
δ1(i)=πi⋅bi(O1), ψ1(i)=0

  * δ1(i): Xác suất lớn nhất khi bắt đầu với trạng thái Si​.

  * ψ1(i): Truy vết trạng thái trước đó, tại thời điểm khởi đầu, giá trị này bằng 0.


**B2: Đệ quy:** Từ t=2 đến T (số lượng từ trong câu):
$$
δt(j)=maxi[δt−1(i)•aij•bj(Ot)],ψt(j)=argmaxi[δt−1(i)•aij]delta_{t}(j) =  max_{i}{leftlbrack delta_{t - 1}(i) bullet a_{ij} bullet b_{j}(O_{t}) rightrbrack, psi_{t}(j) =  argmax_{i}leftlbrack delta_{t - 1}(i) bullet a_{ij} rightrbrack}
$$

  * δt(j): Xác suất lớn nhất dẫn đến trạng thái Sj​ tại thời điểm t.

  * ψt(j): Truy vết trạng thái Si​ tốt nhất trước Sj​.


**B3: Kết thúc:** Tại thời điểm cuối T:

$$
ST*=argmaxiδT(i)S_{T}^{*} =  argmax_{i}{delta_{T}(i)}
$$

**B4: Truy vết:** Từ t=T−1 đến t=1:

$$
St*=ψt+1(St+1*)S_{t}^{*} =  psi_{t + 1}(S_{t + 1}^{*})
$$

St∗=ψt+1(St+1∗)S_t^* = \psi_{t+1}(S_{t+1}^*)St∗​=ψt+1​(St+1∗​)

  * Kết quả là chuỗi nhãn từ loại tối ưu S∗={S1∗,S2∗,…,ST∗}.


## **Ví dụ minh họa**

**Đề bài:** Cho câu quan sát:

O={"The", "cat", "runs"}

Với tập nhãn từ loại:

S={DT (mạo từ),NN (danh từ),VB (động từ)}

Các tham số mô hình:

  * π={P(DT)=0.6,P(NN)=0.3,P(VB)=0.1}.

  * Ma trận chuyển trạng thái:


$$
A=[P(DT→DT)P(DT→NN)P(DT→VB)P(NN→DT)P(NN→NN)P(NN→VB)P(VB→DT)P(VB→NN)P(VB→VB)]=[00.70.30.10.40.50.60.30.1]A =  begin{bmatrix}
P(DT rightarrow  DT) & P(DT rightarrow  NN) & P(DT rightarrow  VB) 
P(NN rightarrow  DT) & P(NN rightarrow  NN) & P(NN rightarrow  VB) 
P(VB rightarrow  DT) & P(VB rightarrow  NN) & P(VB rightarrow  VB)
end{bmatrix} =  begin{bmatrix}
0 & 0.7 & 0.3 
0.1 & 0.4 & 0.5 
0.6 & 0.3 & 0.1
end{bmatrix}
$$

  * Ma trận phát xạ:

$$
B =  begin{bmatrix}
P(O | DT) 
P(O | NN) 
P(O | VB)
end{bmatrix} =  begin{bmatrix}
Pleft( text{"The"} right) = 0.5, P("text{cat"})  =  0.1,
P("runs")  =  0.1 
Pleft( text{"The"} right) = 0.1, P("text{cat"})  =  0.6,
P("runs")  =  0.1 
Pleft( text{"The"} right) = 0.1, P("text{cat"})  =  0.1,
P("runs")  =  0.8
end{bmatrix}
$$


**Giải:**

  * **Khởi tạo:**


$$
δ1(DT)=πDT•bDT("The")=0.6•0.5=0.3delta_{1}(DT) =  pi_{DT} bullet b_{DT}left( text{"The"} right) = 0.6 bullet 0.5 = 0.3
$$
$$
δ1(NN)=πNN•bNN("The")=0.3•0.1=0.03delta_{1}(NN) =  pi_{NN} bullet b_{NN}left( text{"The"} right) = 0.3 bullet 0.1 = 0.03
$$
$$
δ1(VB)=πVB•bVB("The")=0.1•0.1=0.01delta_{1}(VB) =  pi_{VB} bullet b_{VB}left( text{"The"} right) = 0.1 bullet 0.1 = 0.01
$$

  * **Đệ quy (tại** t=2 **):**


$$
delta_{2}(NN) =  maxleftlbrack
delta_{1}(DT) bullet a_{DT rightarrow NN}, delta_{1}(NN) bullet
a_{NN rightarrow NN}, delta_{1}(VB) bullet a_{VB rightarrow NN}
rightrbrack bullet b_{NN}("cat")
$$

  * **Tiếp tục:**  
Lặp lại các bước trên cho đến t=3 để tìm chuỗi nhãn tối ưu.