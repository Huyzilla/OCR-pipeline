# Public_122

# Giới thiệu

Động lực của nghiên cứu xuất phát từ những hạn chế của các phương pháp hiện tại trong việc xử lý các điều kiện ánh sáng phức tạp trong thực tế. Hình ảnh được chụp trong các bối cảnh đa dạng thường gặp phải tình trạng phơi sáng không đồng đều do sự thay đổi của ánh sáng, sự hiện diện của nhiều nguồn sáng, hoặc độ tương phản mạnh giữa các vùng sáng và tối. Các phương pháp truyền thống, như histogram equalization và tone mapping thường dựa trên các mô hình chiếu sáng toàn cục hoặc đơn giản, dẫn đến việc không khôi phục được các chi tiết quan trọng ở cả vùng thừa sáng và thiếu sáng, đặc biệt là trong các cảnh có điều kiện ánh sáng phức tạp.

Các phương pháp deep learning gần đây đã cải thiện đáng kể hiệu năng hiệu chỉnh độ phơi sáng so với các phương pháp truyền thống. Tuy nhiên, hầu hết các mô hình này giả định ánh sáng đồng nhất và không xử lý được sự tương tác giữa nhiều nguồn sáng, điều rất phổ biến trong các cảnh tự nhiên. Tương tự, các mô hình chiếu sáng dựa trên vật lý chủ yếu tập trung vào một nguồn sáng duy nhất, khiến chúng khó áp dụng hiệu quả trong thực tế khi có nhiều nguồn chiếu sáng.

Nghiên cứu này nhằm giải quyết các hạn chế trên bằng cách đề xuất Dual Illumination Estimation. Ý tưởng cốt lõi là mô hình hóa và ước lượng đồng thời hai nguồn sáng chính và phụ, cho phép hiệu chỉnh độ phơi sáng một cách thích ứng và chi tiết trong các điều kiện ánh sáng đa dạng. Phương pháp này không chỉ nâng cao chất lượng hình ảnh được hiệu chỉnh mà còn cung cấp một giải pháp tiền xử lý mạnh mẽ cho các ứng dụng trong nhiếp ảnh, thị giác máy tính, và xử lý ảnh tự động. Bằng cách giải quyết khoảng trống trong các phương pháp hiện có, nghiên cứu kỳ vọng sẽ thiết lập một tiêu chuẩn mới trong hiệu chỉnh độ phơi sáng cho các môi trường phức tạp trong thực tế.

# Mô tả thuật toán

Với một hình ảnh đầu vào, trước tiên quá trình ước lượng chiếu sáng kép (dual illumination estimation) được thực hiện để thu được các ánh sáng tiến (forward illumination) và ngược (reverse illumination). Từ đó, hình ảnh được hiệu chỉnh độ phơi sáng trung gian cho các trường hợp thiếu sáng (underexposure) và thừa sáng (overexposure) sẽ được khôi phục. Tiếp theo, một phương pháp hòa trộn hình ảnh hiệu chỉnh đa phơi sáng (multi-exposure image fusion) hiệu quả sẽ được áp dụng để kết hợp liền mạch các phần được phơi sáng tốt nhất từ hai hình ảnh hiệu chỉnh phơi sáng trung gian, cũng như hình ảnh đầu vào, thành một hình ảnh cuối cùng được phơi sáng đồng đều trên toàn cầu.

![A diagram of a person AI-generated content may be incorrect.](images/image1.png)

_**Tổng quan về thuật toán hiệu chỉnh độ phơi sáng được đề xuất.**_

## Ước lượng chiếu sáng kép (Dual Illumination Estimation)

Phần này mô tả chi tiết kỹ thuật ước lượng chiếu sáng kép. Mục tiêu là ước lượng hai bản đồ chiếu sáng bổ sung: ánh sáng tiến Lf​ và ánh sáng ngược Lr​. Các bản đồ này cho phép hiệu chỉnh các vùng thiếu sáng và thừa sáng của ảnh đầu vào một cách hiệu quả.

Cho ảnh đầu vào I được biểu diễn trong không gian màu RGB với các giá trị cường độ pixel được chuẩn hóa trong khoảng [0,1]. Phương pháp ước lượng chiếu sáng kép dựa trên quan sát rằng có thể tạo ra các ánh sáng bổ sung để cải thiện các vùng phơi sáng khác nhau của ảnh:

  1. Chiếu sáng tiến Lf​: Làm nổi bật và cải thiện các vùng tối hoặc thiếu sáng.

  2. Chiếu sáng ngược Lr​: Tập trung làm giảm các vùng bị thừa sáng.


Quá trình ước lượng Lf​ và Lr​ được thực hiện qua các bước sau:

**Bước 1: Ảnh đảo ngược**

Để tạo ra ánh sáng ngược, ảnh đầu vào III được đảo ngược:

$Iinv=1−II_{inv} = 1 - I$

Phép đảo ngược này thực chất lật các mức cường độ sáng, làm cho các vùng bị thừa sáng trở nên giống như thiếu sáng.

**Bước 2: Mô hình chiếu sáng**

Các bản đồ chiếu sáng được ước lượng bằng cách giải các bài toán tối ưu hóa cho cả Lf​ và Lr​. Các bản đồ này dựa trên mô hình Retinex, tách ảnh thành thành phần phản xạ và chiếu sáng:

$I=R⊙LI = R  odot  L$

Trong đó R là phần phản xạ và L là phần chiếu sáng. Framework dual illumination tính toán Lf​ và Lr​ bằng cách áp dụng các ràng buộc về độ mượt (smoothness) và tính trung thực (fidelity).

**Chiếu sáng tiến L f​:**

$$
Lr=argminL∥I−L⊙R∥2+λΦ(L)L_{r} = argmin_{L}{left| I -  L odot  R right|^{2} + lambda Phi(L)}
$$

trong đó:

  1. $Φ(L)Phi(L)$ là độ mượt (v.d. Total Variation)

  2. $λlambda$ là tham số điều chỉnh mức độ của ràng buộc độ mượt.


**Chiếu sáng ngược L r:​**

Ánh sáng ngược được tính toán tương tự từ ảnh đảo ngược Iinv:

$$
Lr=argminL∥Iinv−L⊙R∥2+λΦ(L)L_{r} = argmin_{L}{left| I_{inv} -  L odot  R right|^{2} + lambda Phi (L)}
$$

**Bước 3: Ước lượng số học**

Các bài toán tối ưu hóa trên được giải theo phương pháp gradient-based, đảm bảo rằng các bản đồ ánh sáng thu được mượt mà đồng thời nắm bắt chính xác điều kiện ánh sáng của ảnh đầu vào.

**Bước 4: Lọc mịn**

Để đảm bảo tính nhất quán giữa Lf​ và Lr​, kỹ thuật lọc song phương (bilateral filtering) được áp dụng. Phương pháp này làm mịn các bản đồ chiếu sáng trong khi vẫn bảo toàn các chi tiết tại biên. Cuối cùng, các bản đồ ánh sáng được chuẩn hóa để đảm bảo tương thích với các bước tiếp theo trong pipeline.

**Mã giả:**

Input: Image I

Output: Forward Illumination L_f, Reverse Illumination L_r

1\. Compute inverted image: I_inv = 1 - I

2\. Initialize L_f, L_r (e.g., with uniform values)

3\. While not converged:

a. Update L_f:

L_f = argmin || I - L_f * R ||^2 + λ * Smoothness(L_f)

b. Update L_r:

L_r = argmin || I_inv - L_r * R ||^2 + λ * Smoothness(L_r)

c. Apply bilateral filter to L_f, L_r

4\. Normalize L_f, L_r

## Trộn đa hình ảnh phơi sáng (Multi-Exposure Image Fusion)

Phần này mô tả chi tiết kỹ thuật hòa trộn hình ảnh đa phơi sáng. Mục tiêu của bước này là kết hợp liền mạch các phần được phơi sáng tốt nhất từ các hình ảnh đã hiệu chỉnh (underexposure-corrected và overexposure-corrected) và ảnh đầu vào để tạo ra một hình ảnh cuối cùng có độ phơi sáng đồng đều trên toàn cầu.

Cho các hình ảnh đầu vào:

Iu​: Hình ảnh đã được hiệu chỉnh vùng thiếu sáng (underexposure-corrected).

Io​: Hình ảnh đã được hiệu chỉnh vùng thừa sáng (overexposure-corrected).

I: Ảnh gốc.

Nhiệm vụ là hợp nhất Iu​, Io​, và I sao cho các vùng được chọn từ mỗi ảnh có độ phơi sáng tối ưu nhất. Quá trình này được thực hiện dựa trên các bản đồ trọng số cục bộ (weight maps) để chỉ định vùng nào sẽ được lấy từ mỗi hình ảnh.

**Bước 1: Tạo bản đồ trọng số cục bộ**

Bản đồ trọng số W được tính toán cho từng hình ảnh Iu​, Io​, và I. Các trọng số này được thiết kế để phản ánh chất lượng phơi sáng cục bộ của từng vùng. Công thức tính trọng số thường dựa trên các đặc trưng như độ tương phản, độ sắc nét và độ sáng cục bộ:

$$
Wx(p)=Contrast(p)•Sharpness(p)⋅Saturation(p)W_{x}(p) = Contrast(p) bullet Sharpness(p) cdot Saturation(p)
$$

Trong đó:

  3. Contrast(p): Đo lường độ tương phản tại điểm ảnh p.

  4. Sharpness(p): Đánh giá độ sắc nét bằng cách sử dụng các bộ lọc gradient.

  5. Saturation(p): Đo mức độ bão hòa màu tại p.


Các bản đồ trọng số được chuẩn hóa để đảm bảo tổng trọng số tại mỗi điểm ảnh bằng 1:

$$
If(p)=∑xŴx(p)⋅Ix(p),x∈{Iu,Io,I}I_{f}(p) = sum_{x}^{}{{widehat{W}}_{x}(p) cdot I_{x}}(p), x in { I_{u},I_{o},I}
$$

Quá trình này đảm bảo rằng mỗi điểm ảnh trong hình ảnh cuối cùng được lấy từ nguồn có chất lượng phơi sáng tốt nhất.

**Bước 3: Tăng độ mượt**

Để đảm bảo tính liên tục và không gây ra hiện tượng đường biên giữa các vùng được chọn từ các hình ảnh khác nhau, các bản đồ trọng số được làm mượt bằng bộ lọc Gaussian hoặc bộ lọc song phương trước khi sử dụng trong bước hòa trộn.

**Mã giả:**

Input: I_u (underexposure-corrected image),

I_o (overexposure-corrected image),

I (original image)

Output: Final globally well-exposed image I_f

1\. Compute local weight maps:

W_u = Contrast(I_u) * Sharpness(I_u) * Saturation(I_u)

W_o = Contrast(I_o) * Sharpness(I_o) * Saturation(I_o)

W_orig = Contrast(I) * Sharpness(I) * Saturation(I)

2\. Normalize weights:

W_u = W_u / (W_u + W_o + W_orig)

W_o = W_o / (W_u + W_o + W_orig)

W_orig = W_orig / (W_u + W_o + W_orig)

3\. Smooth weight maps using Gaussian filter:

W_u = GaussianFilter(W_u)

W_o = GaussianFilter(W_o)

W_orig = GaussianFilter(W_orig)

4\. Fuse images:

I_f = W_u * I_u + W_o * I_o + W_orig * I