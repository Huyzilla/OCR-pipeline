# Public_118

# Giới thiệu

Dimensionality Reduction (giảm chiều dữ liệu) là một kỹ thuật quan trọng trong Machine Learning.  
Dữ liệu thực tế có thể có số chiều rất lớn (hàng nghìn). Việc giảm chiều giúp tiết kiệm lưu trữ, tăng tốc tính toán và có thể coi như nén dữ liệu.  
Một phương pháp tuyến tính cơ bản là Principal Component Analysis (PCA).

# Một chút toán

## Norm 2 của ma trận

||A||_2 = max_x ||Ax||_2 / ||x||_2 (1)

||A||_2 = max_{||x||_2=1} ||Ax||_2 (2)

Giải bằng nhân tử Lagrange cho thấy norm 2 của ma trận chính là singular value lớn nhất của A.  
Vector tương ứng là right-singular vector của A.

## Biểu diễn vector trong các hệ cơ sở khác nhau

x = Uy, y = U^{-1}x (7)

Nếu U trực giao: U^{-1}=U^T, do đó y = U^T x.

## Trace

Một số tính chất:  
\- trace(A) = trace(A^T)  
\- trace(kA) = k trace(A)  
\- trace(AB) = trace(BA)  
\- ||A||_F^2 = trace(A^T A)  
\- trace(A) = tổng các trị riêng của A

## Kỳ vọng và ma trận hiệp phương sai

Một chiều: x̄ = (1/N) Σ x_n, σ^2 = (1/N) Σ (x_n − x̄)^2

Đa chiều: x̄ = (1/N) Σ x_n, S = (1/N) (X − x̄1^T)(X − x̄1^T)^T

# Principal Component Analysis (PCA)

Mục tiêu: Tìm hệ cơ sở trực chuẩn sao cho phương sai dữ liệu tập trung ở K thành phần đầu.  
Dữ liệu chuẩn hoá: Ẋ = X − x̄1^T  
Ma trận hiệp phương sai: S = (1/N)ẊẊ^T  
  
Hàm mất mát: J = Σ_{i=K+1}^D u_i^T S u_i  
Tối ưu tương đương chọn K vector riêng ứng với K trị riêng lớn nhất của S.

# Các bước PCA

  * Tính kỳ vọng x̄

  * Chuẩn hoá dữ liệu: Ẋ = X − x̄1^T

  * Tính ma trận hiệp phương sai S

  * Tính trị riêng & vector riêng, sắp xếp λ giảm dần

  * Chọn K vector riêng lớn nhất → U_K

  * Tính toạ độ mới: Z = U_K^T Ẋ

  * Xấp xỉ khôi phục: x ≈ U_K z + x̄