---
session: 8
title_fa: شبکه‌های عصبی و بردارهای کلمات
title_en: Neural Networks & Word Embeddings
summary_fa: گذر از ان‌گرام به مدل‌های عصبی، ساختار و ریاضیات تک‌نورون و توابع فعال‌ساز، شبکه‌های پیش‌خور، روش‌های بردارسازی کلمات، انتشار به عقب و شبکه‌های برگشتی RNN با چالش‌های گرادیان.
lecturer: دکتر مهرنوش شمس‌فرد
tags: [شبکه عصبی, بردارهای کلمات, RNN, انتشار به عقب, FFNN]
---

## ۱. گذر از ان‌گرام به شبکه‌های عصبی | From N-grams to Neural Networks

در جلسات گذشته، مدل‌های زبانی ان‌گرام ابزار اصلی پیش‌بینی کلمهٔ بعدی بودند. جملهٔ زیر را در نظر بگیرید:

«من امروز برای خرید کتاب به [جای خالی]…»

ذهن انسان بر اساس معنی کلمات پیشین و بافت، کلماتی مانند «کتابخانه» یا «باغ» را به عنوان ادامهٔ احتمالی بازشناسی می‌کند. در مدل‌های ان‌گرام، این مسئله از طریق فراوانی‌های پیکره حل می‌شد؛ مثلاً در مدل ۳-گرام:

```math
P(w_i \mid w_{i-2}, w_{i-1}) = \frac{C(w_{i-2}, w_{i-1}, w_i)}{C(w_{i-2}, w_{i-1})}
```

الگوریتم، میزان تکرار ترکیب سه‌کلمه‌ای (مانند «کتاب به کتابخانه») را نسبت به کل تکرارهای ترکیب دوکلمه‌ای («کتاب به») می‌سنجید و کلمه‌ای با بالاترین احتمال را انتخاب می‌کرد.

::: warning محدودیت‌های بنیادین ان‌گرام
۱) **پنجرهٔ بافت ثابت (Fixed Context Window):** مدل‌های ان‌گرام فقط ۲ یا ۳ کلمهٔ قبل را می‌بینند و وابستگی‌های بلندمدت متن را کاملاً از دست می‌دهند.

۲) **وابستگی شدید به دادگان آموزشی (Corpus Dependence):** اگر ترکیب کلمه‌ای خاص در پیکرهٔ آموزشی نباشد، احتمال آن صفر برآورد می‌شود (مشکل Data Sparsity).

۳) **عدم درک شباهت معنایی:** مدل‌های ان‌گرام ارتباط معنایی میان کلمات مترادف (مانند «کتابخانه» و «کتاب‌فروشی») را نمی‌فهمند و هر کلمه را نمادی کاملاً مستقل می‌دانند.
:::

این چالش‌ها سبب حرکت پردازش زبان طبیعی به سمت شبکه‌های عصبی مصنوعی (Artificial Neural Networks — ANN) شد.


## ۲. ساختار و ریاضیات تک‌نورون | Single Neuron

پایه‌ای‌ترین واحد پردازشی، نورون واحد است: ورودی‌ها $(x_1, x_2, \dots, x_n)$ هر یک در وزن متناظر $(w_1, w_2, \dots, w_n)$ ضرب شده، جمع می‌شوند و بایاس (b) به آن اضافه می‌شود تا متغیر خطی z ساخته شود:

```math
z = \sum_{i=1}^{n} w_i x_i + b = w_1 x_1 + w_2 x_2 + \dots + w_n x_n + b
```

ترکیب خطی محض نمی‌تواند روابط پیچیده و غیرخطی زبان را مدل کند؛ از این رو z وارد تابع فعال‌ساز (Activation Function) می‌شود:

```svg
<svg viewBox="0 0 270 124" fill="none" aria-hidden="true">
  <text x="6" y="30" font-size="12" fill="#cfe0ff" font-family="Vazirmatn, sans-serif">x₁</text>
  <text x="6" y="62" font-size="12" fill="#cfe0ff" font-family="Vazirmatn, sans-serif">x₂</text>
  <text x="6" y="96" font-size="12" fill="#cfe0ff" font-family="Vazirmatn, sans-serif">xₙ</text>
  <line x1="32" y1="26" x2="96" y2="50" stroke="rgba(158,184,255,.55)" stroke-width="1.2"/>
  <line x1="32" y1="58" x2="96" y2="58" stroke="rgba(158,184,255,.55)" stroke-width="1.2"/>
  <line x1="32" y1="92" x2="96" y2="68" stroke="rgba(158,184,255,.55)" stroke-width="1.2"/>
  <circle cx="114" cy="60" r="17" fill="rgba(122,166,255,.15)" stroke="rgba(158,184,255,.7)" stroke-width="1.3"/>
  <text x="114" y="65" text-anchor="middle" font-size="14" fill="#eaf2ff" font-family="Vazirmatn, sans-serif">Σ</text>
  <text x="100" y="102" font-size="12" fill="#cfe0ff" font-family="Vazirmatn, sans-serif">b</text>
  <line x1="105" y1="97" x2="112" y2="78" stroke="rgba(158,184,255,.55)" stroke-width="1.2"/>
  <path d="M133 56h20m-6-6 6 6-6 6" stroke="#7aa6ff" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="166" y="45" width="48" height="30" rx="8" fill="rgba(122,166,255,.15)" stroke="rgba(158,184,255,.7)" stroke-width="1.3"/>
  <text x="190" y="64" text-anchor="middle" font-size="13" fill="#eaf2ff" font-family="Vazirmatn, sans-serif">σ</text>
  <path d="M216 60h26" stroke="rgba(158,184,255,.55)" stroke-width="1.2"/>
  <path d="M242 54h8l-5 6 5 6h-8" stroke="#7aa6ff" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="256" y="65" font-size="12" fill="#cfe0ff" font-family="Vazirmatn, sans-serif">y</text>
</svg>
```

### ۲.۱. توابع فعال‌ساز غیرخطی

| نام تابع | رابطهٔ ریاضی | بازهٔ خروجی | ویژگی‌ها و کاربردها |
|---|---|---|---|
| سیگموئید (Sigmoid) | $\sigma(z) = \frac{1}{1 + e^{-z}}$ | [0, 1] | مناسب برای احتمال‌دهی و دسته‌بندی دوحالته (مثبت/منفی) |
| تانژانت هیپربولیک (Tanh) | $\tanh(z) = \frac{e^z - e^{-z}}{e^z + e^{-z}}$ | [-1, 1] | تقارن حول صفر؛ مناسب برای لایه‌های پنهان |
| یکسوکنندهٔ خطی (ReLU) | $\text{ReLU}(z) = \max(0, z)$ | [0, +∞) | مقدار منفی را صفر می‌کند و مثبت را عیناً برمی‌گرداند؛ سرعت بالا |

### ۲.۲. مثال عددی

بردار ورودی $x = [0.5, 0.6, 0.1]$، وزن‌ها $w = [0.3, 0.3, 0.9]$، بایاس $b = 0.5$ و تابع فعال‌ساز سیگموئید:

**گام ۱ — مقدار خطی z:**

```math
z = (0.5 \times 0.3) + (0.6 \times 0.3) + (0.1 \times 0.9) + 0.5 = 0.15 + 0.18 + 0.09 + 0.5 = 0.92
```

**گام ۲ — اعمال سیگموئید:**

```math
y = \sigma(0.92) = \frac{1}{1 + e^{-0.92}} \approx \frac{1}{1 + 0.3985} \approx 0.715
```


## ۳. شبکه‌های عصبی پیش‌خور | Feedforward Neural Networks

با قرار دادن چند نورون در یک لایه و زنجیره‌سازی چند لایه روی هم، شبکهٔ عصبی چندلایه (Multi-Layer Perceptron / FFNN) ساخته می‌شود:

```svg
<svg viewBox="0 0 280 150" fill="none" aria-hidden="true">
  <g stroke="rgba(158,184,255,.4)" stroke-width="1">
    <line x1="56" y1="30" x2="128" y2="25"/><line x1="56" y1="30" x2="128" y2="55"/><line x1="56" y1="30" x2="128" y2="85"/><line x1="56" y1="30" x2="128" y2="115"/>
    <line x1="56" y1="75" x2="128" y2="25"/><line x1="56" y1="75" x2="128" y2="55"/><line x1="56" y1="75" x2="128" y2="85"/><line x1="56" y1="75" x2="128" y2="115"/>
    <line x1="56" y1="120" x2="128" y2="25"/><line x1="56" y1="120" x2="128" y2="55"/><line x1="56" y1="120" x2="128" y2="85"/><line x1="56" y1="120" x2="128" y2="115"/>
    <line x1="150" y1="25" x2="218" y2="55"/><line x1="150" y1="25" x2="218" y2="95"/>
    <line x1="150" y1="55" x2="218" y2="55"/><line x1="150" y1="55" x2="218" y2="95"/>
    <line x1="150" y1="85" x2="218" y2="55"/><line x1="150" y1="85" x2="218" y2="95"/>
    <line x1="150" y1="115" x2="218" y2="55"/><line x1="150" y1="115" x2="218" y2="95"/>
  </g>
  <g fill="rgba(122,166,255,.18)" stroke="rgba(158,184,255,.7)" stroke-width="1.2">
    <circle cx="56" cy="30" r="10"/><circle cx="56" cy="75" r="10"/><circle cx="56" cy="120" r="10"/>
    <circle cx="150" cy="25" r="10"/><circle cx="150" cy="55" r="10"/><circle cx="150" cy="85" r="10"/><circle cx="150" cy="115" r="10"/>
    <circle cx="218" cy="55" r="10"/><circle cx="218" cy="95" r="10"/>
  </g>
  <text x="56" y="146" text-anchor="middle" font-size="11" fill="#9db8ff" font-family="Vazirmatn, sans-serif">لایهٔ ورودی</text>
  <text x="150" y="146" text-anchor="middle" font-size="11" fill="#9db8ff" font-family="Vazirmatn, sans-serif">لایهٔ پنهان</text>
  <text x="218" y="146" text-anchor="middle" font-size="11" fill="#9db8ff" font-family="Vazirmatn, sans-serif">لایهٔ خروجی</text>
</svg>
```

- **لایهٔ ورودی (Input Layer):** بردار داده‌های ورودی را دریافت می‌کند.
- **لایه‌های پنهان (Hidden Layers):** ویژگی‌های انتزاعی و پیچیده را استخراج می‌کنند؛ افزایش تعداد آن‌ها باعث «عمیق شدن» شبکه (Deep Learning) می‌شود.
- **لایهٔ خروجی (Output Layer):** خروجی نهایی مدل (مانند برچسب کلاس یا احتمال کلمهٔ بعدی) را تولید می‌کند.

در شبکه‌های پیش‌خور، جریان اطلاعات فقط در جهت مستقیم (از ورودی به خروجی) حرکت می‌کند و هیچ حلقهٔ بازگشتی وجود ندارد.


## ۴. بردارسازی کلمات | Word Embeddings

برای ورود کلمات به شبکه‌های عصبی، باید به بردارهای عددی تبدیل شوند:

۱) **کدگذاری یک‌داغ (One-Hot Encoding):** برداری به طول کل واژگان که فقط در ایندکس کلمهٔ موردنظر ۱ و در سایر خانه‌ها ۰ است.
   - **محدودیت:** بردارهای بسیار پراکنده (Sparse) و عریض؛ عدم نمایش ارتباط معنایی میان کلمات.

۲) **ماتریس کلمه-مدرک (Word-Document Matrix):** حضور یا تعداد تکرار کلمه در مدارک مختلف ثبت می‌شود.

۳) **بردارهای متراکم معنایی (Dense Word Embeddings):** کلمات به بردارهای متراکم با ابعاد پایین‌تر (مثلاً ۳۰۰ بعد) تبدیل می‌شوند که ویژگی‌های معنایی و هم‌آیی کلمات را حفظ می‌کنند (مانند Word2Vec یا مدل‌های زبانی).

### ۴.۱. ترکیب بردارهای ورودی در FFNN

اگر ورودی چند کلمه باشد (مثلاً جملهٔ ۳کلمه‌ای)، بردارها به یکی از دو روش به یک بردار واحد تبدیل می‌شوند:

- **الحاق (Concatenation):** چسباندن بردارهای کلمات پشت سر هم.
- **میانگین‌گیری (Averaging):** میانگین مؤلفه‌های بردارهای کلمات.

در لایهٔ خروجی برای دسته‌بندی چندکلاسه یا پیش‌بینی کلمه، از تابع **Softmax** استفاده می‌شود تا توزیع احتمال روی تمام کلمات واژگان به دست آید.


## ۵. آموزش شبکه: انتشار به عقب | Backpropagation

فرایند آموزش شامل سه گام اصلی است:

۱) **گذر پیش‌رو (Forward Pass):** ورودی وارد شبکه شده و خروجی پیش‌بینی‌شده محاسبه می‌شود.

۲) **محاسبهٔ تابع زیان (Loss Function):** تفاوت خروجی پیش‌بینی‌شده با برچسب واقعی (Ground Truth) ارزیابی می‌شود (مثلاً با Cross-Entropy Loss).

۳) **انتشار به عقب (Backpropagation) و کاهش گرادیان (Gradient Descent):** خطا از انتهای شبکه به لایه‌های ابتدایی بازمی‌گردد. با قاعدهٔ زنجیره‌ای دیفرانسیل، گرادیان خطا نسبت به تک‌تک وزن‌ها محاسبه و وزن‌ها به‌روزرسانی می‌شوند:

```math
w_{new} = w_{old} - \eta \, \frac{\partial L}{\partial w}
```

که در آن $\eta$ نرخ یادگیری (Learning Rate) است.


## ۶. شبکه‌های عصبی برگشتی | Recurrent Neural Networks

### ۶.۱. چرا ترتیب کلمات اهمیت دارد؟

در FFNN کلمات به صورت بردار ایزوله یا مجموعه‌ای ثابت وارد می‌شوند و ترتیب زمانی حفظ نمی‌شود؛ در حالی که در زبان طبیعی تغییر ترتیب، معنا را کاملاً عوض می‌کند:

«علیرضا رضا را دید» ≠ «رضا علیرضا را دید»

RNN برای پردازش توالی‌های زبانی با طول متغیر و حفظ ترتیب زمانی طراحی شده است.

### ۶.۲. وضعیت پنهان (Hidden State)

در هر گام زمانی t، کلمهٔ جاری $x_t$ به همراه وضعیت پنهان گام قبل $h_{t-1}$ — که حافظهٔ کلمات گذشته است — وارد نورون می‌شوند:

```math
h_t = \tanh(W_h \, h_{t-1} + W_x \, x_t + b_h)

y_t = \text{Softmax}(W_y \, h_t + b_y)
```

### ۶.۳. گشودن شبکه در زمان

اگر سلول RNN در گام‌های زمانی t=0, t=1, t=2, … باز شود، دیده می‌شود که اطلاعات از گام‌های اول به گام‌های بعدی منتقل می‌شوند:

```svg
<svg viewBox="0 0 310 132" fill="none" aria-hidden="true">
  <g>
    <rect x="18" y="34" width="60" height="38" rx="9" fill="rgba(122,166,255,.14)" stroke="rgba(158,184,255,.7)" stroke-width="1.3"/>
    <text x="48" y="50" text-anchor="middle" font-size="11" fill="#eaf2ff" font-family="Vazirmatn, sans-serif">h(t−1)</text>
    <text x="48" y="65" text-anchor="middle" font-size="9" fill="#9db8ff" font-family="Vazirmatn, sans-serif">سلول RNN</text>
    <rect x="125" y="34" width="60" height="38" rx="9" fill="rgba(122,166,255,.14)" stroke="rgba(158,184,255,.7)" stroke-width="1.3"/>
    <text x="155" y="50" text-anchor="middle" font-size="11" fill="#eaf2ff" font-family="Vazirmatn, sans-serif">h(t)</text>
    <text x="155" y="65" text-anchor="middle" font-size="9" fill="#9db8ff" font-family="Vazirmatn, sans-serif">سلول RNN</text>
    <rect x="232" y="34" width="60" height="38" rx="9" fill="rgba(122,166,255,.14)" stroke="rgba(158,184,255,.7)" stroke-width="1.3"/>
    <text x="262" y="50" text-anchor="middle" font-size="11" fill="#eaf2ff" font-family="Vazirmatn, sans-serif">h(t+1)</text>
    <text x="262" y="65" text-anchor="middle" font-size="9" fill="#9db8ff" font-family="Vazirmatn, sans-serif">سلول RNN</text>
  </g>
  <g stroke="#7aa6ff" stroke-width="1.3">
    <path d="M80 53h43m-6-6 6 6-6 6"/>
    <path d="M187 53h43m-6-6 6 6-6 6"/>
  </g>
  <g stroke="rgba(158,184,255,.55)" stroke-width="1.2">
    <line x1="48" y1="98" x2="48" y2="74"/>
    <line x1="155" y1="98" x2="155" y2="74"/>
    <line x1="262" y1="98" x2="262" y2="74"/>
    <line x1="48" y1="32" x2="48" y2="12"/>
    <line x1="155" y1="32" x2="155" y2="12"/>
    <line x1="262" y1="32" x2="262" y2="12"/>
  </g>
  <g font-size="10.5" fill="#9db8ff" font-family="Vazirmatn, sans-serif">
    <text x="48" y="112" text-anchor="middle">x(t−1)</text>
    <text x="155" y="112" text-anchor="middle">x(t)</text>
    <text x="262" y="112" text-anchor="middle">x(t+1)</text>
    <text x="48" y="8" text-anchor="middle">y(t−1)</text>
    <text x="155" y="8" text-anchor="middle">y(t)</text>
    <text x="262" y="8" text-anchor="middle">y(t+1)</text>
  </g>
</svg>
```


## ۷. معماری‌های RNN و محدودیت‌ها | RNN Architectures & Limitations

### ۷.۱. الگوهای معماری

| نوع معماری | توصیف | کاربرد در NLP |
|---|---|---|
| یک به یک (One-to-One) | یک ورودی، یک خروجی | شبکهٔ پیش‌خور استاندارد |
| چند به یک (Many-to-One) | دریافت توالی کلمات، تولید یک خروجی تکی | تحلیل احساسات (Sentiment Analysis)، دسته‌بندی متن |
| چند به چند هم‌طول (Many-to-Many Same Length) | یک برچسب به ازای هر کلمهٔ ورودی | برچسب‌زنی نحوی (POS Tagging)، شناسایی موجودیت‌های نامدار (NER) |
| چند به چند نابرابر (Encoder-Decoder) | توالی با طول N به توالی با طول M | ترجمهٔ ماشینی (Machine Translation)، خلاصه‌سازی متن |

### ۷.۲. چالش‌های بنیادین RNN ساده

۱) **کاهش توجه و فراموشی گذشته (Recency Bias & Information Dilution):** با طولانی شدن توالی (مثلاً در جملهٔ «What time is it?»)، اطلاعات کلمات ابتدایی در اثر ضرب‌های متوالی کمرنگ و فراموش می‌شوند (عدم پشتیبانی از Long-Term Dependencies).

۲) **گرادیان محو شونده و جهنده (Vanishing & Exploding Gradients):** در انتشار به عقب در زمان (BPTT)، به دلیل ضرب‌های مکرر ماتریس وزن‌ها در گام‌های زمانی طولانی:

- اگر مشتقات کوچک‌تر از ۱ باشند، گرادیان به سمت صفر می‌رود (Vanishing Gradient) و وزن‌های لایه‌های اولیه به‌روزرسانی نمی‌شوند.
- اگر مشتقات بزرگ‌تر از ۱ باشند، گرادیان به‌شدت رشد می‌کند و منفجر می‌شود (Exploding Gradient) و استقرار مدل مختل می‌گردد.

### ۷.۳. معرفی اجمالی LSTM

برای حل مشکل وابستگی‌های بلندمدت و گرادیان محو شونده، شبکه‌های LSTM (Long Short-Term Memory) معرفی شدند که با درگاه‌های مدیریت حافظه (Forget Gate، Input Gate، Output Gate) کنترل می‌کنند چه اطلاعاتی حفظ و چه اطلاعاتی فراموش شوند.


## ۸. واژه‌نامه | Glossary

| فارسی | English | معنی کوتاه |
|---|---|---|
| شبکهٔ عصبی مصنوعی | Artificial Neural Network (ANN) | مدل محاسباتی الهام‌گرفته از نورون‌ها |
| تابع فعال‌ساز | Activation Function | نگاشت غیرخطی خروجی نورون |
| سیگموئید / تانژانت هیپربولیک / یکسوکنندهٔ خطی | Sigmoid / Tanh / ReLU | سه تابع فعال‌ساز پرکاربرد |
| شبکهٔ عصبی پیش‌خور | Feedforward Neural Network (FFNN) | جریان اطلاعات فقط به سمت جلو |
| وضعیت پنهان | Hidden State | بردار حافظهٔ گام‌های قبلی در RNN |
| بردارهای کلمات | Word Embeddings | بازنمایی متراکم معنایی کلمات |
| کدگذاری یک‌داغ | One-Hot Encoding | بردار صفر و یک به طول واژگان |
| انتشار به عقب | Backpropagation | بازگشت خطا و محاسبهٔ گرادیان وزن‌ها |
| کاهش گرادیان | Gradient Descent | به‌روزرسانی وزن‌ها در خلاف جهت گرادیان |
| شبکهٔ عصبی برگشتی | Recurrent Neural Network (RNN) | پردازش توالی با حفظ ترتیب زمانی |
| گشودن در طول زمان | Unrolling over Time | باز کردن سلول RNN در گام‌های زمانی |
| گرادیان محو شونده / جهنده | Vanishing / Exploding Gradient | میل گرادیان به صفر یا رشد انفجاری |
| حافظهٔ کوتاه‌مدت طولانی | Long Short-Term Memory (LSTM) | RNN با درگاه‌های مدیریت حافظه |
