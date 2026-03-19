# Public_102

## 1\. Định nghĩa

![A diagram of a network AI-generated content may be incorrect.](images/image1.png)

Hình 1. Linear-Chain CRFs dạng factor với các ô vuông là các hàm phụ thuộc giữa các nút

Gọi X là biến ngẫu nhiên đại diện cho chuỗi dữ liệu đầu vào cần được gán nhãn, Y là biến ngẫu nhiên đại diện cho chuỗi nhãn tương ứng với chuỗi dữ liệu X. Tất cả các thành phần $YiY_{i}$ của Y thuộc một tập nhãn hữu hạn $𝒴mathcal{Y}$ (tập các nhãn có thể có). $ΩxOmega_{x}$ là các trường hợp có thể có của chuỗi X, $ΩyOmega_{y}$ là các trường hợp có thể có của chuỗi nhãn Y.

Giả định cả X và Y đều được coi là biến ngẫu nhiên phân phối chung (jointly distributed), nghĩa là chúng có mối liên hệ xác suất với nhau, và xác suất $P(X,Y)P(X,Y)$ là dương nghiêm ngặt ($P(X=x,Y=y)>0,∀x,yP(X =  x,Y = y) > 0, forall x, y$).

CRFs [8] là một mô hình phân biệt, tập trung vào việc xây dựng mô hình xác suất có điều kiện P(Y|X). CRFs dự đoán chuỗi nhãn Y dựa trên chuỗi dữ liệu X đã cho. CRFs không cố gắng mô hình hóa xác suất của X (tức là P(X)), mà chỉ quan tâm đến xác suất của Y khi biết X.

Định nghĩa: Cho đồ thị $G=(V,E)G = (V,E)$ sao cho $Y=(Yv)v∈VY = left( Y_{v} right)_{v  in  V}$, nghĩa là $YY$ được chỉ mục hóa theo các đỉnh của đồ thị $GG$. Khi đó, cặp $(X,Y)(X,Y)$ là một trường ngẫu nhiên điều kiện (conditional random fields - CRFs) trong trường hợp, khi biết $XX$, các biến ngẫu nhiên $YvY_{v}$​ thỏa mãn tính chất Markov đối với đồ thị:

$$
P(Yv|X,Yw,w≠v)=P(Yv|X,Yw,w∼v)Pleft( Y_{v} middle| X, Y_{w},w neq v right) =  Pleft( Y_{v} middle| X, Y_{w},wsim v right)
$$

trong đó $w∼vwsim v$ có nghĩa là $ww$ và $vv$ là các đỉnh kề nhau trong đồ thị $GG$. Hay nói cách khác trạng thái của các đỉnh trong đồ thị chỉ phụ thuộc vào các điểm lân cận.

=> CRFs là một trường hợp đặc biệt của MRF, trong có các nút có thể chia thành 2 tập riêng biệt X, Y. Và xác suất của chuỗi nhãn Y được xác định dựa trên toàn bộ chuỗi quan sát X. Do X là các biến quan sát lên cấu trúc đồ thị của X là tùy ý và Y và các biến y ∈ Y có thể phụ thuộc vào bất kì biến nào trong X.

Trong trường hợp CRFs có X, Y là các chuỗi X = (X1, …, Xn), Y = (Y1,…, Yn) và đồ thị G là cây mà các đỉnh có bậc không quá 2 (chuỗi tuyến tính) thì được gọi là trường ngẫu nhiên có điều kiện tuyến tính (Linear-Chain CRFs).

![A diagram of a network AI-generated content may be incorrect.](images/image2.png)

Hình 2. Ví dụ minh họa Linear-Chain CRFs trong bài toán gán nhãn thực thể có tên

Hình 2 là một ví dụ về Linear-Chain CRFs được sử dụng trong bài toán gán nhãn thực thể có tên (tìm xem từ nào là tên riêng – PER, từ nào là tên địa danh – LOC). Ở đây, các từ trong câu đầu vào cần được gán nhãn sẽ có vai trò là chuỗi X, các nhãn cần được gán cho từng từ trong câu đầu vào sẽ là chuỗi Y. Các nhãn này sẽ nhận một trong các giá trị: PER-Tên riêng, LOC-Địa điểm, O-Không xác định. Theo tích chất Markov thì nhãn của từ hiện tại chỉ phụ thuộc vào nhãn trước, nhãn sau và câu đầu vào.

## 2\. Xây dựng mô hình xác suất P(Y|X) 

Với giả định $P(X=x,Y=y)P(X =  x,Y = y)$ là dương nghiêm ngặt, theo định lý Hammersley–Clifford [9], ta có:

$$
E(x,y)=−∑ci∈Cfi(ci)E(x,y) =   - sum_{c_{i} in C}^{}f_{i}left( c_{i} right)
$$

$$
P(X=x,Y=y)=1Ze−E(x,y)P(X =  x,Y = y) =  frac{1}{Z}e^{- E(x,y)}
$$

$$
Z=∑x∈Ωx,y∈Ωye−E(x,y){Z =  sum_{x  in  Omega_{x}, y  in  Omega_{y}}^{}e^{- E(x,y)}}
$$

Trong đó C là tập tất cả các nhóm đầy đủ của đồ thị G (một **nhóm đầy đủ** trong đồ thị vô hướng là một tập hợp các đỉnh mà giữa tất cả các cặp đỉnh trong tập hợp đó đều tồn tại một cạnh), $fif_{i}$ là hàm năng lượng của cụm $cic_{i}$ chỉ ra khả năng xảy ra các mối quan hệ trong cụm. Z là hằng số chuẩn hóa để tạo phân phối xác suất hợp lệ (<1). $E(x,y)E(x,y)$ là hàm năng lượng được sử dụng để đánh giá mức độ "tốt" của một cặp giá trị $(x,y)(x,y)$ cụ thể của các biến ngẫu nhiên X, Y. Cặp giá trị $(x,y)(x,y)$ có $E(x,y)E(x,y)$ thấp hơn được coi là tốt hơn.

Dựa vào công thức trên kết hợp định lý Bayes, ta suy ra phân phối của chuỗi nhãn Y khi biết X có dạng sau:

$$
P(Y=y|X=x)=P(Y=y,X=x)P(X=x)=e−E(x,y)Z∑y′∈Ωye−E(x,y′)ZPleft( Y = y middle| X =  x right) =  frac{P(Y = y,X =  x)}{P(X =  x)} =  frac{frac{e^{- E(x,y)}}{Z}}{frac{sum_{y^{'} in  Omega_{y}}^{}e^{- Eleft( x,y^{'} right)}}{Z}}
$$

$=e−E(x,y)Z(x)=  frac{e^{- E(x,y)}}{Z(x)}$
$$
=exp(∑ci∈Cfi(ci))Z(x)=   frac{expleft( sum_{c_{i} in C}^{}f_{i}left( c_{i} right) right)}{Z(x)}
$$

$$
Z(x)=∑y′∈Ωye−E(x,y′)Z(x) =  sum_{y^{'} in  Omega_{y}}^{}e^{- E(x,y')}
$$

Với Linear-Chain CRFs, tập các cụm là 2 đỉnh của các cạnh và các đỉnh lẻ, khi đó, ta có:

$$
E(x,y)=−(∑(i−1,i)∈Ef(yi−1,yi,x,i)+∑yi∈yg(yi,x,i))E(x,y) =   - left( sum_{(i - 1, i) in E}^{}fleft( y_{i - 1}, y_{i}, x,i right) +  sum_{y_{i} in y}^{}gleft( y_{i}, x,i right) right)
$$

Để đơn giản, ta thêm 2 nhãn vào đầu và cuối chuỗi nhãn: Y0 = <Start>. Trong Linear-Chain CRFs, hàm năng lượng cho các cạnh là tổng hợp các hàm đặc trưng cạnh $fkf_{k}$ và hàm năng lượng cho đỉnh là tổng hợp các hàm đặc trưng của đỉnh $gkg_{k}$.

$$
E(x,y)=−(∑i=1n∑kλkfk(yi−1,yi,x,i)+∑i=1n∑kμkgk(yi,x,i))E(x,y) =   - left( sum_{i = 1}^{n}{sum_{k}^{}{lambda_{k} f_{k}left( y_{i - 1}, y_{i}, x,i right)}} +  sum_{i = 1}^{n}{sum_{k}^{}{mu_{k} g_{k}left( y_{i}, x,i right)}} right)
$$

$$
pθ(Y=y|X=x)=exp(∑i=1n∑kλkfk(yi−1,yi,x,i)+∑i=1n∑kμkgk(yi,x,i))Zθ(x)p_{theta}left( Y = y middle| X =  x right) =   frac{expleft( sum_{i = 1}^{n}{sum_{k}^{}{lambda_{k} f_{k}left( y_{i - 1}, y_{i}, x,i right)}} +  sum_{i = 1}^{n}{sum_{k}^{}{mu_{k} g_{k}left( y_{i}, x,i right)}} right)}{Z_{theta}(x)}
$$

$$
Zθ(x)=∑y′∈Ωyexp(∑i=1n∑kλkfk(y′i−1,y′i,x,i)+∑i=1n∑kμkgk(y′i,x,i))Z_{theta}(x) =  sum_{y^{'} in  Omega_{y}}^{}{expleft( sum_{i = 1}^{n}{sum_{k}^{}{lambda_{k} f_{k}left( {y'}_{i - 1}, {y'}_{i}, x,i right)}} +  sum_{i = 1}^{n}{sum_{k}^{}{mu_{k} g_{k}left( {y'}_{i}, x,i right)}} right)}
$$

Các hàm đặc trưng $fkf_{k}$và $gkg_{k}$ được cho trước và cố định, thường là chỉ báo cho 1 đặc trưng ví dụ 1 hàm đặc trưng sẽ trả về giá trị 1 khi $XiX_{i}$ viết hoa chữ cái đầu và $YiY_{i}$ có nhãn là “N” ngược lại sẽ trả về 0.

Trọng số $λklambda_{k}$, $μkmu_{k}$ của hàm đặc trưng là một hệ số điều chỉnh mức độ ảnh hưởng của hàm đặc trưng đến năng lượng của cấu hình. Trọng số càng cao, hàm đặc trưng càng có ảnh hưởng lớn đến xác suất của chuỗi nhãn.

## 3\. Linear-Chain CRFs dạng ma trận 

Giả sử, $$
𝒴={C1,…,Cl}mathcal{Y} =  left{ C_{1},ldots,C_{l} right}
$$, $$
𝒴′=𝒴∪{<Start>}mathcal{Y}^{'} =  mathcal{Y cup}left{ < Start > right}
$$. Xác xuất có điều kiện của chuỗi Y có thể được biểu diễn dưới dạng ma trận. Tại mỗi vị trí i trong chuỗi quan sát x, ta định nghĩa một ma trận biến ngẫu nhiên kích thước $$
|𝒴′|×|𝒴′|left| mathcal{Y'} right| times left| mathcal{Y'} right|
$$, $$
Mi(x)=[Mi(Cj,Ck|x)],Cj,Ck∈𝒴M_{i}(x) =  leftlbrack M_{i}left( C_{j},C_{k} middle| x right) rightrbrack,  C_{j},C_{k} in  mathcal{Y}
$$.

Mỗi phần tử $Mi(Cj,Ck|x)M_{i}left( C_{j},C_{k} middle| x right)$ đại diện cho một giá trị xác suất chưa chuẩn hóa. $Mi(x)M_{i}(x)$ là biến ngẫu nhiên mà giá trị phụ thuộc vào chuỗi quan sát X.

$$
Mi(Cj,Ck|x)=exp(∑kλkfk(Yi−1=Cj,yi=Ck,x,i)+∑kμkgk(Yi=Cj,x,i))M_{i}left( C_{j},C_{k} middle| x right)  =  expleft( sum_{k}^{}{lambda_{k}f_{k}left( Y_{i - 1} = C_{j}, y_{i} = C_{k}, x,i right)} +  sum_{k}^{}{mu_{k}g_{k}left( Y_{i} = C_{j}, x,i right)} right)
$$

Với cách biểu diễn trên, $Zθ(x)Z_{theta}(x)$ có thể viết lại dưới dạng sau với $1|𝒴′|×11_{left| mathcal{Y'} right| times 1}$ là ma trận kích thước $|𝒴′|left| mathcal{Y'} right|$ hàng và 1 cột có các giá trị bằng 1:

$$
Zθ(x)=(M1(x)×M2(x)×...×Mn+1×1|𝒴′|×1)0,0Z_{theta}(x) =  left( M_{1}(x) times M_{2}(x) times ... times {M_{n + 1} times 1}_{left| mathcal{Y'} right| times 1} right)_{0,0}
$$

Công thức xác suất có điều kiện có thể biểu diễn dưới dạng ma trận:

$$
pθ(Y=y|X=x)=∏i=1nMi(yi−1,yi|x)((∏i=1nMi(x))×1|𝒴′|×1)0,0p_{theta}left( Y = y middle| X =  x right) =   frac{prod_{i = 1}^{n}{M_{i}left( y_{i - 1},y_{i} middle| x right)}}{left( left( prod_{i = 1}^{n}{M_{i}(x)} right){times 1}_{left| mathcal{Y'} right| times 1} right)_{0, 0}}
$$

Biểu diễn này hữu ích trong việc huấn luyện và suy luận mô hình CRFs.

![A diagram of a graph AI-generated content may be incorrect.](images/image3.png)

Hình 3. Linear-Chain CRFs biều diễn dưới dạng factor với các factor được coi là ma trận chuyển đổi

Hình 3 là một ví dụ mình họa của linear-Chain CRFs biểu diễn dưới dạng factor cho bài toán POS tiếng Việt (gán nhãn động từ - v, danh từ - n, đại từ - p, trạng từ - d). Ở đây, câu đầu vào có 5 từ và mỗi 1 từ sẽ được gán nhãn từ loại tương ứng. Chuỗi từ loại chính là chuỗi Y. Giữa mỗi cặp nhãn cần gán kề nhau sẽ có một ma trận thể hiện khả năng mà giá trị nhán được gán khi biết nhãn của từ liền kề.