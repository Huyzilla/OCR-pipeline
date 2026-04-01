# Public_119

### **1. Giới thiệu**

Trong hai bài viết trước, PCA (unsupervised) giữ lại tổng phương sai lớn nhất nhưng không dùng nhãn. Trong phân lớp (supervised), tận dụng nhãn thường cho kết quả tốt hơn. Ví dụ chiếu lên các hướng d1 (gần PC1) và d2 (gần thành phần phụ): d1 có thể làm hai lớp chồng lấn, trong khi d2 tách tốt hơn cho classification. Điều này cho thấy giữ lại nhiều phương sai nhất không phải lúc nào cũng tốt cho phân lớp. LDA ra đời để tìm phép chiếu tuyến tính (projection matrix) tối đa hóa khả năng phân biệt (discriminant). Với C lớp, số chiều mới không vượt quá C−1.

#### **2. LDA cho bài toán với 2 classes**

# **2.1 Ý tưởng cơ bản**

Discriminant tốt khi: (i) mỗi lớp tập trung (within-class variance nhỏ), (ii) các lớp cách xa nhau (between-class variance lớn).

### **2.2 Xây dựng hàm mục tiêu**

*Ký hiệu: dữ liệu x\_n, phép chiếu y\_n = w^T x\_n.*

Kỳ vọng mỗi lớp: m\_k = (1/N\_k) ∑\_{n∈C\_k} x\_n, k=1,2. (1)

Hiệu kỳ vọng sau chiếu: m\_1 − m\_2 ⇒ w^T(m\_1−m\_2). (2)

Within-class variances (không lấy trung bình): s\_k^2 = ∑\_{n∈C\_k} (y\_n − m\_k)^2. (3)

Ma trận between-class: S\_B = (m\_1−m\_2)(m\_1−m\_2)^T. (5)

Ma trận within-class: S\_W = ∑\_{k=1}^2 ∑\_{n∈C\_k} (x\_n−m\_k)(x\_n−m\_k)^T. (6)

### **Hàm mục tiêu Fisher (2 lớp):**

$$J(w) = (w^T S_B w) / (w^T S_W w).$$
 (4,7)

# **2.3 Nghiệm tối ưu (Fisher's linear discriminant)**

*Đạo hàm và sắp xếp lại:*

$$S_W^{-1} S_B w = J(w) w.$$
 (10)

#### **Chọn nghiệm tỷ lệ:**

$$w = \alpha S_W^{-1}(m_1 - m_2), \alpha \neq 0.$$
 (11)

### **3. LDA cho multi-class classification**

Phép chiếu tuyến tính: y = W^T x, W ∈ R^{D×D′}. Không dùng bias.

### **Within-class tổng quát:**

$$s_W = trace(W^T S_W W)$$
,  $v\acute{o}i S_W = \sum_{k=1}^{\infty} C \sum_{n \in C_k} (x_n - m_k)(x_n - m_k)^T$ . (17–19)

#### Between-class tổng quát:

$$s_B = trace(W^T S_B W), \ v\acute{o}i \ S_B = \sum_{k=1}^C N_k (m_k - m)(m_k - m)^T. \ (21-22)$$

# Hàm mục tiêu multi-class:

$$J(W) = trace(W^T S B W) / trace(W^T S W W).$$

Điều kiên tối ưu bậc nhất:

$$S_W^{-1} S_B W = J W.$$
 (24)

Các cột của W là các eigenvectors ứng với các trị riêng lớn nhất của  $S \ W^{-1} S B$ .

 $B\mathring{o} \mathring{d}\grave{e}$ :  $rank(S \ B) \leq C - 1 \Rightarrow s\mathring{o} chi\grave{e}u t\acute{o}i \mathring{d}a sau LDA \leq C - 1$ .

### Ví du nhanh (Python, phác thảo)

- Tạo dữ liệu 2 lớp: X0,  $X1 \in R^{N \times D}$ ; tính m0, m1.
  S B = (m0 m1)(m0)•  $S B = (m0 - m1)(m0 - m1)^T$ ;  $S W = \sum (x - m k)(x - m k)^T$ .
  - W tù eigenvectors của inv(S W) @ S B: sánh sklearn.discriminant analysis.LDA.

### Thảo luân

LDA là phương pháp supervised giảm chiều và/hoặc phân lớp: tối ưu small within-class & large between-class. Số chiều tối đa sau LDA là  $\leq$  C-1. Giả định thường gặp: phân phối gần Gaussian, các ma trận hiệp phương sai giữa các lớp gần nhau. LDA tốt khi các lớp gần linearly separable; kém hiệu quả nếu không tách tuyến tính.

2025-09-28 17.48.20 AI Race

2025-09-28 17.48.20\_AI Race