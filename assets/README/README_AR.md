<div align="center">

<img src="../../assets/logo.png" alt="DeepTutor" width="140" style="border-radius: 15px;">

# DeepTutor: تعليم شخصي أصلي قائم على الوكلاء

<a href="https://trendshift.io/repositories/17099" target="_blank"><img src="https://trendshift.io/api/badge/repositories/17099" alt="HKUDS%2FDeepTutor | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

<p align="center">
  <a href="../../README.md"><img alt="English" height="40" src="https://img.shields.io/badge/English-CDCFD4"></a>&nbsp;
  <a href="README_CN.md"><img alt="简体中文" height="40" src="https://img.shields.io/badge/简体中文-CDCFD4"></a>&nbsp;
  <a href="README_JA.md"><img alt="日本語" height="40" src="https://img.shields.io/badge/日本語-CDCFD4"></a>&nbsp;
  <a href="README_ES.md"><img alt="Español" height="40" src="https://img.shields.io/badge/Español-CDCFD4"></a>&nbsp;
  <a href="README_FR.md"><img alt="Français" height="40" src="https://img.shields.io/badge/Français-CDCFD4"></a>&nbsp;
  <a href="README_AR.md"><img alt="Arabic" height="40" src="https://img.shields.io/badge/Arabic-BCDCF7"></a>&nbsp;
  <a href="README_RU.md"><img alt="Русский" height="40" src="https://img.shields.io/badge/Русский-CDCFD4"></a>&nbsp;
  <a href="README_HI.md"><img alt="Hindi" height="40" src="https://img.shields.io/badge/Hindi-CDCFD4"></a>&nbsp;
  <a href="README_PT.md"><img alt="Português" height="40" src="https://img.shields.io/badge/Português-CDCFD4"></a>&nbsp;
  <a href="README_TH.md"><img alt="Thai" height="40" src="https://img.shields.io/badge/Thai-CDCFD4"></a>&nbsp;
  <a href="README_PL.md"><img alt="Polski" height="40" src="https://img.shields.io/badge/Polski-CDCFD4"></a>
</p>

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)](../../LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/HKUDS/DeepTutor?style=flat-square&color=brightgreen)](https://github.com/HKUDS/DeepTutor/releases)
[![arXiv](https://img.shields.io/badge/arXiv-2604.26962-b31b1b?style=flat-square&logo=arxiv&logoColor=white)](https://arxiv.org/abs/2604.26962)

[![Discord](https://img.shields.io/badge/Discord-Community-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.gg/eRsjPgMU4t)
[![Feishu](https://img.shields.io/badge/Feishu-Group-00D4AA?style=flat-square&logo=feishu&logoColor=white)](../../Communication.md)
[![WeChat](https://img.shields.io/badge/WeChat-Group-07C160?style=flat-square&logo=wechat&logoColor=white)](https://github.com/HKUDS/DeepTutor/issues/78)

[الميزات](#key-features) · [البدء](#get-started) · [استكشاف](#explore-deeptutor) · [TutorBot](#tutorbot) · [CLI](#deeptutor-cli) · [متعدد المستخدمين](#multi-user) · [المجتمع](#community)

</div>

---

> 🤝 **نرحّب بجميع أنواع المساهمات!** راجع [دليل المساهمة](../../CONTRIBUTING.md) لاستراتيجية الفروع ومعايير البرمجة وكيفية البدء.
>
> 🗺️ **خارطة الطريق** متتبَّعة بشكل مفتوح في [`HKUDS/DeepTutor#498`](https://github.com/HKUDS/DeepTutor/issues/498) — علّق هناك للتصويت على العناصر أو اقتراح عناصر جديدة.

### 📦 الإصدارات

> **[2026.5.21]** [v1.4.0-beta](https://github.com/HKUDS/DeepTutor/releases/tag/v1.4.0-beta) — منضدة Memory ثلاثية الطبقات (L1/L2/L3)، إعادة بناء كل قدرات الدردشة على محرك وكيل واحد، RAG حصراً على LlamaIndex، وواجهة موحدة لـ Settings + Capabilities.

> **[2026.5.10]** [v1.3.10](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.10) — استرداد CORS لـ Docker البعيد، `DISABLE_SSL_VERIFY` عبر مزودي SDK، اقتباسات أكثر أماناً لكتل الكود، وإضافة Matrix E2EE اختيارية.

> **[2026.5.9]** [v1.3.9](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.9) — دعم Zulip و NVIDIA NIM لـ TutorBot، توجيه أكثر أماناً لنماذج التفكير، `deeptutor start`، تلميحات الشريط الجانبي، وتجانس مخزن الجلسات.

> **[2026.5.8]** [v1.3.8](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.8) — نشر اختياري متعدد المستخدمين مع مساحات عمل معزولة لكل مستخدم، صلاحيات إدارية، مسارات مصادقة، ووصول وقت تشغيل ذو نطاق محدد.

<details>
<summary><b>الإصدارات السابقة (قبل أكثر من أسبوعين)</b></summary>

> **[2026.5.4]** [v1.3.7](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.7) — إصلاحات نماذج التفكير/المزودين، تاريخ فهرسة Knowledge مرئي، تفريغ وتحرير قوالب Co-Writer أكثر أماناً.

> **[2026.5.3]** [v1.3.6](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.6) — اختيار النماذج المبني على الكاتالوج للدردشة و TutorBot، إعادة فهرسة RAG أكثر أماناً، إصلاحات حد الرموز لـ OpenAI Responses، والتحقق من محرر Skills.

> **[2026.5.2]** [v1.3.5](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.5) — إعدادات إطلاق محلية أكثر سلاسة، استعلامات RAG أكثر أماناً، مصادقة embedding محلية أوضح، وتحسين الوضع الداكن في Settings.

> **[2026.5.1]** [v1.3.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.4) — استمرار دردشة صفحة الكتاب وتدفقات إعادة البناء، مراجع من الدردشة إلى الكتاب، معالجة لغة/تفكير أقوى، وتقوية استخراج وثائق RAG.

> **[2026.4.30]** [v1.3.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.3) — دعم embeddings NVIDIA NIM و Gemini، سياق Space موحد (تاريخ الدردشة/المهارات/الذاكرة)، لقطات الجلسة، ومرونة إعادة فهرسة RAG.

> **[2026.4.29]** [v1.3.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.2) — عناوين URL شفافة لنقاط نهاية embedding، مرونة إعادة فهرسة RAG لمتجهات الإصرار غير الصالحة، تنظيف ذاكرة مخرجات نموذج التفكير، وإصلاح وقت تشغيل Deep Solve.

> **[2026.4.28]** [v1.3.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.1) — الاستقرار: توجيه RAG والتحقق من embedding أكثر أماناً، إصرار Docker، إدخال آمن لـ IME، ومتانة Windows/GBK.

> **[2026.4.27]** [v1.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.0) — فهارس KB موسومة بإصدارات مع تدفق إعادة الفهرسة، مساحة عمل Knowledge معاد بناؤها، اكتشاف تلقائي لـ embeddings مع محولات جديدة، ومركز Space.

> **[2026.4.25]** [v1.2.5](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.5) — مرفقات دردشة دائمة مع درج معاينة الملفات، خطوط أنابيب القدرات الواعية للمرفقات، وتصدير Markdown لـ TutorBot.

> **[2026.4.25]** [v1.2.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.4) — مرفقات نصية/كود/SVG، Setup Tour بأمر واحد، تصدير Markdown للدردشة، وواجهة إدارة KB المدمجة.

> **[2026.4.24]** [v1.2.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.3) — مرفقات الوثائق (PDF/DOCX/XLSX/PPTX)، عرض كتل التفكير، محرر قوالب Soul، وحفظ Co-Writer إلى notebook.

> **[2026.4.22]** [v1.2.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.2) — نظام Skills التي ينشئها المستخدم، إصلاح أداء إدخال الدردشة، بدء تلقائي لـ TutorBot، واجهة مكتبة الكتب، والتصور بملء الشاشة.

> **[2026.4.21]** [v1.2.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.1) — حدود الرموز لكل مرحلة، إعادة توليد الرد عبر جميع نقاط الدخول، وإصلاحات التوافق مع RAG و Gemma.

> **[2026.4.20]** [v1.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.0) — مُجمِّع «الكتاب الحي» Book Engine، Co-Writer متعدد الوثائق، تصورات HTML تفاعلية، و@-mention لـ Question Bank.

> **[2026.4.18]** [v1.1.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.2) — علامة تبويب Channels مدفوعة بالمخطط، توحيد خط أنابيب RAG واحد، وتصدير prompts الدردشة.

> **[2026.4.17]** [v1.1.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.1) — «أجب الآن» العالمي، مزامنة تمرير Co-Writer، لوحة إعدادات موحدة، وزر Stop للبث المباشر.

> **[2026.4.15]** [v1.1.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0) — إعادة هيكلة كتلة الرياضيات LaTeX، فحص تشخيصي لـ LLM، وإرشادات Docker + LLM محلي.

> **[2026.4.14]** [v1.1.0-beta](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0-beta) — جلسات قابلة للتسجيل، سمة Snow، نبضات WebSocket وإعادة اتصال تلقائية، وإعادة هيكلة سجل embedding.

> **[2026.4.13]** [v1.0.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.3) — Question Notebook مع إشارات مرجعية وفئات، Mermaid في Visualize، اكتشاف عدم تطابق embedding، توافق Qwen/vLLM، دعم LM Studio و llama.cpp، وسمة Glass.

> **[2026.4.11]** [v1.0.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.2) — توحيد البحث مع احتياطي SearXNG، إصلاح تبديل المزود، وإصلاحات تسرب الموارد في الواجهة الأمامية.

> **[2026.4.10]** [v1.0.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.1) — قدرة Visualize (Chart.js/SVG)، منع التكرار في quiz، ودعم نموذج o4-mini.

> **[2026.4.10]** [v1.0.0-beta.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.4) — تتبع تقدم embedding مع إعادة المحاولة في حد المعدل، إصلاحات تبعيات عبر المنصات، وإصلاح التحقق من MIME.

> **[2026.4.8]** [v1.0.0-beta.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.3) — SDK أصلي لـ OpenAI/Anthropic (إسقاط litellm)، دعم Windows Math Animator، تحليل JSON قوي، وi18n صيني كامل.

> **[2026.4.7]** [v1.0.0-beta.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.2) — إعادة تحميل الإعدادات الساخن، مخرجات MinerU المتداخلة، إصلاح WebSocket، والحد الأدنى Python 3.11+.

> **[2026.4.4]** [v1.0.0-beta.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.1) — إعادة كتابة معمارية أصلية للوكلاء (~200 ألف سطر): نموذج إضافات Tools + Capabilities، CLI و SDK، TutorBot، Co-Writer، التعلم الموجَّه، والذاكرة الدائمة.

> **[2026.1.23]** [v0.6.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.6.0) — استمرار الجلسات، التحميل التزايدي للوثائق، استيراد مرن لخط أنابيب RAG، وتوطين صيني كامل.

> **[2026.1.18]** [v0.5.2](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.2) — دعم Docling لـ RAG-Anything، تحسين نظام التسجيل، وإصلاحات الأخطاء.

> **[2026.1.15]** [v0.5.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.0) — تكوين خدمة موحد، اختيار خط أنابيب RAG لكل قاعدة معرفة، إصلاح توليد الأسئلة، وتخصيص الشريط الجانبي.

> **[2026.1.9]** [v0.4.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.4.0) — دعم LLM و embedding متعدد المزودين، صفحة رئيسية جديدة، فصل وحدة RAG، وإعادة هيكلة متغيرات البيئة.

> **[2026.1.5]** [v0.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.3.0) — معمارية PromptManager موحدة، CI/CD على GitHub Actions، وصور Docker مبنية مسبقاً على GHCR.

> **[2026.1.2]** [v0.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.2.0) — نشر Docker، الترقية إلى Next.js 16 و React 19، تعزيز أمان WebSocket، وإصلاحات الثغرات الحرجة.

</details>

### 📰 الأخبار

> **[2026.4.19]** 🎉 وصلنا إلى 20 ألف نجمة بعد 111 يوماً! شكراً على الدعم المذهل — نحن ملتزمون بالتكرار المستمر نحو تعليم شخصي وذكي حقاً للجميع.

> **[2026.4.10]** 📄 ورقتنا متاحة الآن على arXiv! اقرأ [النسخة الأولية](https://arxiv.org/abs/2604.26962) لمعرفة المزيد عن التصميم والأفكار وراء DeepTutor.

> **[2026.4.4]** لم نلتقِ منذ فترة! ✨ DeepTutor v1.0.0 هنا أخيراً — تطور أصلي قائم على الوكلاء يتميز بإعادة كتابة معمارية كاملة، TutorBot، وتبديل وضع مرن تحت رخصة Apache-2.0. يبدأ فصل جديد!

> **[2026.2.6]** 🚀 وصلنا إلى 10 آلاف نجمة في 39 يوماً فقط! شكراً جزيلاً لمجتمعنا الرائع على الدعم!

> **[2026.1.1]** عام جديد سعيد! انضم إلى [Discord](https://discord.gg/eRsjPgMU4t) أو [WeChat](https://github.com/HKUDS/DeepTutor/issues/78) أو [Discussions](https://github.com/HKUDS/DeepTutor/discussions) — لنرسم معاً مستقبل DeepTutor!

> **[2025.12.29]** تم إطلاق DeepTutor رسمياً!


<a id="key-features"></a>
## ✨ الميزات الرئيسية

**أسطح العمل**

- Chat — Chat و Solve و Quiz و Research و Visualize تتشارك جلسة واحدة، قاعدة معرفة، وتاريخ اقتباس، حتى تتمكن من التصعيد في منتصف المحادثة دون فقدان السياق.
- Co-Writer — مساحة عمل Markdown بعرض مقسم حيث يمكن إعادة كتابة أي تحديد أو توسيعه أو اختصاره، اختيارياً مع الاستناد إلى KB أو الويب. تُحفظ المسودات مباشرة في notebooks.
- Book Engine — خط أنابيب متعدد الوكلاء يجمع موادك في «كتب حية» تفاعلية بـ 13 نوع كتلة: اختبارات، بطاقات تعليمية، خطوط زمنية، رسوم بيانية للمفاهيم، عارض GeoGebra مدمج، رسوم متحركة، والمزيد. الصفحات مبصمة بـ KB، حتى يمكن اكتشاف الانحراف.

**مكتبتك**

- Knowledge Bases — مجموعات موسومة بإصدارات وجاهزة لـ RAG، من البداية إلى النهاية على LlamaIndex. كل عملية (إعادة) فهرسة متتبَّعة، قابلة للمقارنة والإرجاع.
- Space — مكتبة مراجعة شخصية تجمع تاريخ الدردشة، notebooks، بنك الأسئلة، وskills التي ينشئها المستخدم (`SKILL.md`) والتي تغير شخصية DeepTutor.
- ذاكرة ثلاثية الطبقات — آثار L1 بإلحاق فقط، حقائق L2 منسقة حسب السطح مع اقتباسات، وتوليف L3 عبر الأسطح. منضدة قابلة للفحص ورسم بياني للذاكرة يتيحان لك تدقيق *لماذا* يعرف DeepTutor ما يعرفه.

**القابلية للتوسيع والتحكم**

- أدوات قابلة للتركيب — RAG، البحث على الويب، تنفيذ الكود، التفكير، العصف الذهني، البحث عن المقالات، تحليل GeoGebra، ومساعدو الدردشة (`ask_user`, `web_fetch`, `write_note`, `list_notebook`, `github_query`). تتصل خوادم MCP جنباً إلى جنب مع الأدوات المدمجة.
- TutorBots شخصية — معلمون دائمون ومستقلون، لكل منهم مساحة عمله الخاصة، soul، skills، وقنوات (Telegram، Discord، Slack، Matrix، Zulip، …). مبنية على [nanobot](https://github.com/HKUDS/nanobot).
- Settings موحدة — منضدة مسودة / Apply واحدة للمظهر، النماذج، embeddings، البحث، القدرات، الذاكرة، خوادم MCP، والأدوات، مع تتبع مشترك للتكلفة لكل استدعاء.
- CLI أصلية للوكلاء — كل قدرة، KB، جلسة، و TutorBot على بعد أمر واحد؛ مخرجات غنية للبشر، JSON منظم للوكلاء. سلِّم [`SKILL.md`](../../SKILL.md) لأي LLM يستخدم الأدوات، وسيتمكن من قيادة DeepTutor بنفسه.
- مصادقة اختيارية — معطلة افتراضياً؛ فعّلها للنشر متعدد المستخدمين مع bcrypt + JWT، لوحة إدارة، و sidecar اختياري لـ PocketBase / OAuth.

---

<a id="get-started"></a>
## 🚀 البدء

يحتوي DeepTutor الآن على أربعة مسارات تثبيت متوازية. جميعها تستخدم نفس بنية تكوين وقت التشغيل:

- توجد الإعدادات في `data/user/settings/` تحت مساحة عملك الحالية، أو تحت `DEEPTUTOR_HOME` / `deeptutor start --home` عندما تختار واحدة صراحةً.
- يخزن `model_catalog.json` ملفات مزودي النماذج، عناوين URL الأساسية، مفاتيح API، النماذج النشطة، إعدادات embedding، وإعدادات البحث.
- يخزن `system.json` منافذ الإطلاق، قاعدة API العامة، CORS، TLS، وخيارات المرفقات.
- يخزن `auth.json` مفتاح التبديل الاختياري للمصادقة وتجزئة بيانات اعتماد الإقلاع.
- يخزن `integrations.json` sidecars اختيارية مثل PocketBase.
- لم يعد `.env` في جذر المشروع يستخدم كملف تكوين للتطبيق.

للحصول على التطبيق المحلي الكامل، الترتيب الموصى به هو **اختر مساحة عمل ← ثبّت ← `deeptutor init` ← `deeptutor start`**.

### الخيار 1 — تثبيت DeepTutor

استخدم هذا عندما تريد تطبيق الويب المحلي الكامل والـ CLI دون استنساخ المستودع.

```bash
mkdir -p my-deeptutor
cd my-deeptutor
pip install -U deeptutor
deeptutor init
deeptutor start
```

> 🧪 **تجرب v1.4.0 beta؟** يطبّع PyPI `1.4.0-beta` إلى `1.4.0b0`، لذا فإن `pip install -U deeptutor` سيبقى على أحدث إصدار مستقر. اشترك في الإصدار التجريبي بأي من:
>
> ```bash
> pip install --pre -U deeptutor      # أحدث إصدار تجريبي
> pip install -U deeptutor==1.4.0b0   # تثبيت دقيق على v1.4.0-beta
> ```

يكتب `deeptutor init` التكوين تحت `data/user/settings/` في الدليل الذي تشغّله منه. يطلب منك:

- منفذ الخلفية، الافتراضي `8001`
- منفذ الواجهة الأمامية، الافتراضي `3782`
- ربط مزود LLM، عنوان URL الأساسي، مفتاح API، واسم النموذج
- مزود embedding اختياري لـ Knowledge Base / RAG

بعد `deeptutor start`، افتح عنوان URL للواجهة الأمامية المطبوع في الطرفية. مع المنافذ الافتراضية، هذا العنوان هو [http://127.0.0.1:3782](http://127.0.0.1:3782).

أبقِ طرفية `deeptutor start` مفتوحة. اضغط `Ctrl+C` في تلك الطرفية لإيقاف كل من الخلفية والواجهة الأمامية.

ملاحظات:

- يبدأ `deeptutor start` خلفية FastAPI وواجهة Next.js المعبأة معاً.
- لا يتطلب تطبيق الويب المعبأ `git clone` أو `npm install`، لكنه لا يزال يحتاج إلى وقت تشغيل Node.js 20+ محلي.

### الخيار 2 — التثبيت من المصدر

استخدم هذا عندما تطوّر DeepTutor أو تريد التشغيل مباشرة من checkout.
استخدم Python 3.11+ و Node.js 22 LTS للحصول على أقرب تطابق مع CI و Docker.

**1. استنساخ المستودع**

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
```

**2. إنشاء بيئة Python**

macOS / Linux مع `venv`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Windows PowerShell مع `venv`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Conda / Miniconda:

```bash
conda create -n deeptutor python=3.11
conda activate deeptutor
python -m pip install --upgrade pip
```

**3. تثبيت الحزمة المحلية وتبعيات الواجهة الأمامية**

```bash
python -m pip install -e .
cd web
npm ci --legacy-peer-deps
cd ..
```

**4. التكوين والبدء**

```bash
deeptutor init
deeptutor start
```

إذا أبلغ `deeptutor start` عن واجهة أمامية موجودة لا تستجيب، أزل ملفات القفل القديمة وابدأ مرة أخرى:

```bash
rm -f web/.next/dev/lock web/.next/lock
deeptutor start
```

إضافات مفيدة للمطورين:

```bash
pip install -e ".[dev]"             # أدوات الاختبارات/lint
pip install -e ".[tutorbot]"        # محرك TutorBot + SDKs القنوات
pip install -e ".[matrix]"          # قناة Matrix بدون E2EE/libolm
pip install -e ".[matrix-e2e]"      # Matrix E2EE؛ يتطلب libolm
pip install -e ".[math-animator]"   # إضافة Manim؛ تتطلب LaTeX/ffmpeg/مكتبات النظام
```

### الخيار 3 — Docker

استخدم هذا عندما تريد تطبيق الويب الكامل في حاوية واحدة. تُنشر الصور إلى GitHub Container Registry:

- `ghcr.io/hkuds/deeptutor:latest` — إصدار مستقر
- `ghcr.io/hkuds/deeptutor:pre` — إصدار تجريبي عند توفره

```bash
docker pull ghcr.io/hkuds/deeptutor:latest
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

ثم افتح [http://127.0.0.1:3782](http://127.0.0.1:3782). يتم تخزين التكوين، مفاتيح API، السجلات، ملفات مساحة العمل، الذاكرة، وقواعد المعرفة في الحجم `deeptutor-data` تحت `/app/data`.

#### الاتصال بـ Ollama أو خدمات المضيف الأخرى

داخل حاوية Docker، يشير `localhost` إلى الحاوية نفسها، وليس جهازك المضيف. إذا كنت تشغّل Ollama أو LM Studio أو llama.cpp أو vLLM أو خدمة نموذج أخرى على المضيف، استخدم أحد هذه النهج.

الخيار A — بوابة المضيف، موصى به لتشغيلات Docker العادية:

```bash
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  --add-host=host.docker.internal:host-gateway \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

ثم في **DeepTutor Settings → Models**، عيّن عنوان URL الأساسي للمزود إلى `host.docker.internal`:

- نقطة نهاية Ollama LLM: `http://host.docker.internal:11434/v1`
- نقطة نهاية embedding Ollama: `http://host.docker.internal:11434/api/embed`
- LM Studio: `http://host.docker.internal:1234/v1`
- llama.cpp: `http://host.docker.internal:8080/v1`

الخيار B — شبكة المضيف، Linux فقط:

```bash
docker run --network=host \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

للتشغيل في الخلفية:

```bash
docker run -d --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
docker logs -f deeptutor
```

### الخيار 4 — CLI فقط

استخدم هذا عندما لا تحتاج إلى واجهة الويب.

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor

python3 -m venv .venv-cli
source .venv-cli/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ./packaging/deeptutor-cli
deeptutor init --cli
deeptutor chat
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv-cli
.\.venv-cli\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ./packaging/deeptutor-cli
deeptutor init --cli
deeptutor chat
```

يستخدم `deeptutor init --cli` نفس بنية `data/user/settings/` كما في التطبيق الكامل، ولكن يغيّر سلوك المعالج:

- يتخطى مطالبات منافذ الخلفية/الواجهة الأمامية لأن الاستخدام مع CLI فقط لا يبدأ تطبيق الويب.
- لا يزال يكتب ملفات `system.json` و `auth.json` و `integrations.json` و `model_catalog.json` و `main.yaml` و `agents.yaml` الافتراضية.
- لا يزال يطلب مزود LLM والنموذج النشط.
- يسأل عما إذا كان سيُكوّن embeddings، ولكن الإجابة الافتراضية هي `لا`؛ اختر `نعم` إذا كنت تخطط لاستخدام `deeptutor kb ...` أو أدوات RAG.

أوامر CLI شائعة:

```bash
deeptutor chat
deeptutor chat --capability deep_solve --tool rag --kb my-kb
deeptutor run chat "اشرح تحويل فورييه"
deeptutor run deep_solve "حُل x^2 = 4" --tool rag --kb my-kb
deeptutor kb create my-kb --doc textbook.pdf
deeptutor kb list
deeptutor memory show
deeptutor config show
```

### مرجع التكوين

| الملف | الغرض |
|:---|:---|
| `data/user/settings/model_catalog.json` | ملفات مزودي LLM و embedding والبحث؛ مفاتيح API؛ النماذج النشطة |
| `data/user/settings/system.json` | منافذ الخلفية/الواجهة الأمامية، قاعدة API العامة، CORS، التحقق من SSL، دليل المرفقات |
| `data/user/settings/auth.json` | مفتاح تبديل المصادقة الاختياري، اسم المستخدم، تجزئة كلمة المرور، إعدادات الرمز/الكوكي |
| `data/user/settings/integrations.json` | إعدادات تكامل PocketBase و sidecar الاختيارية |
| `data/user/settings/interface.json` | تفضيلات لغة/سمة/الشريط الجانبي لواجهة المستخدم |
| `data/user/settings/main.yaml` | افتراضيات سلوك وقت التشغيل وحقن المسارات |
| `data/user/settings/agents.yaml` | إعدادات درجة الحرارة والرموز لقدرات/أدوات |

<a id="explore-deeptutor"></a>
## 📖 استكشاف DeepTutor

<div align="center">
<img src="../../assets/figs/deeptutor-architecture.png" alt="DeepTutor Architecture" width="800">
</div>

تعيد إعادة هيكلة v1.4.0-beta تنظيم DeepTutor حول **خمسة أسطح أساسية** — Chat و Co-Writer و Book و Knowledge و Space — بالإضافة إلى **Memory ثلاثية الطبقات** التي توجد تحتها جميعاً ومنضدة عمل **Settings** موحدة تعرض كل مفتاح ضبط. تتركب القدرات (Solve / Quiz / Research / Visualize) والأدوات (RAG، الويب، الكود، التفكير، العصف الذهني، البحث عن المقالات، `ask_user`, `web_fetch`, `write_note`, `list_notebook`, `github_query`) بحرية فوقها.

### 💬 Chat — مساحة عمل ذكية موحدة

<div align="center">
<img src="../../assets/figs/dt-chat.png" alt="Chat Workspace" width="800">
</div>

خيط واحد، خمسة أوضاع، أي أداة. منتقي القدرات موجود في المؤلِّف؛ تنتقل معك نفس الجلسة، قاعدة المعرفة، المرفقات، والمراجع عبر الأوضاع — انتقل من سؤال عابر إلى حل متعدد الوكلاء، إلى اختبار، إلى تقرير بحثي كامل، دون فقدان السياق.

| الوضع | ما يفعله | مبني على |
|:---|:---|:---|
| **Chat** | محادثة مرنة مع أي أداة؛ اختر من RAG، البحث على الويب، تنفيذ الكود، التفكير العميق، العصف الذهني، البحث عن المقالات، تحليل GeoGebra. | RAG مدعوم بـ LlamaIndex + سجل الأدوات |
| **Solve** | خطة متعددة الخطوات → تحقيق → حل → تحقق، مع اقتباسات مصادر دقيقة. | محرك وكيل (`deep_solve`) |
| **Quiz** | توليد أسئلة مُتحقق منها تلقائياً مستندة إلى KB الخاصة بك؛ ينشئ مؤلف دردشة متابعة لكل سؤال. | محرك وكيل (`deep_question`) |
| **Research** | يفكك موضوعاً إلى مواضيع فرعية، ويرسل وكلاء متوازية عبر RAG / الويب / arXiv، وينتج تقريراً مع اقتباسات وتنقيحات تكرارية في وضع الإلحاق. | `pipeline.py` معاد بناؤه (~45% أصغر، الاقتباسات + التقارير التكرارية محفوظة) |
| **Visualize** | يولد رسوم SVG، مخططات Chart.js، رسوم بيانية Mermaid، صفحات HTML تفاعلية، **أو** فيديوهات/قصص مصورة Manim — يختار المحلل `render_type` الصحيح. | خط أنابيب Visualize (Animator مدمج) |

**أدوات دردشة جديدة** صدرت مع إعادة الهيكلة: `ask_user` (يطرح سؤالاً توضيحياً منظماً في منتصف الدور)، `web_fetch` (يسحب عنوان URL محدد إلى السياق)، `write_note` / `list_notebook` (يحفظ ويسرد سجلات notebook من سطح الدردشة)، و `github_query` (عمليات بحث في issue / PR / المستودع). تبقى الأدوات **منفصلة عن سير العمل** — كل وضع يسمح لك بتفعيل الأدوات أو تعطيلها لكل دور.

تحمل الجلسة أيضاً **مخزون مصادر تراكمي** عبر الأدوار، بحيث تبقى الاقتباسات من ضربات RAG / الويب السابقة قابلة لإعادة الاستخدام لاحقاً في نفس المحادثة.

### ✍️ Co-Writer — مساحة عمل كتابة AI متعددة الوثائق

<div align="center">
<img src="../../assets/figs/dt-cowriter.png" alt="Co-Writer" width="800">
</div>

Co-Writer هو منضدة عمل Markdown بعرض مقسم (المحرر الخام على اليسار، المعاينة الحية على اليمين) للملاحظات والتقارير والدروس التعليمية ومسودات بمساعدة AI. كل وثيقة تعيش في مساحة عملها الخاصة مع حفظ تلقائي، Markdown قابل للتنزيل، و**حفظ في Notebook** بنقرة واحدة.

حدد أي نص واختر **إعادة كتابة** أو **توسيع** أو **اختصار** — كل إجراء يُنفذ كتعديل وكيل متتبَّع يمكنه اختيارياً السحب من قاعدة معرفة أو الويب.

### 📖 Book Engine — «كتب حية» تفاعلية

<div align="center">
<img src="../../assets/figs/dt-book.png" alt="Book Engine" width="800">
</div>

أعطِ DeepTutor موضوعاً، وجّهه إلى قاعدة معرفتك، وسينتج كتاباً منظماً وتفاعلياً — ليس تصديراً ثابتاً، بل وثيقة حية يمكنك قراءتها، اختبار نفسك بها، ومناقشتها في السياق.

خلف الكواليس، يتعامل خط أنابيب متعدد الوكلاء مع العمل الشاق: اقتراح مخطط، استرداد المصادر ذات الصلة من KB، تركيب شجرة فصول، تخطيط كل صفحة، وتجميع كل كتلة. تبقى أنت في السيطرة — راجع الاقتراح، أعد ترتيب الفصول، وتحدث بجانب أي صفحة.

تتجمع الصفحات من 13 نوع كتلة — نص، استدعاء، اختبار، بطاقات تعليمية، كود، شكل، غوص عميق، رسوم متحركة، عرض تفاعلي (يشمل الآن **عارض GeoGebra**)، خط زمني، رسم بياني للمفاهيم، قسم، وملاحظة المستخدم.

### 📚 Knowledge Bases — مكتبات وثائق جاهزة لـ RAG

<div align="center">
<img src="../../assets/figs/dt-kb.png" alt="Knowledge Bases" width="800">
</div>

مساحة عمل مخصصة لمجموعات الوثائق التي تشغّل RAG. كل قاعدة معرفة لها أربع علامات تبويب:

- **Files** — تصفح المصادر المرفوعة، وعاين PDFs في الموقع، وشاهد الحجم/الحالة لكل ملف.
- **Add documents** — أضف PDFs، ملفات Office (DOCX / XLSX / PPTX)، Markdown، نص عادي، ونطاق واسع من أنواع ملفات الكود/البيانات. تُوجَّه الوثائق تلقائياً إلى المستخرج المناسب.
- **Index versions** — كل عملية (إعادة) فهرسة هي إصدار متتبَّع. ارجع إلى فهرس سابق، قارن نماذج embedding، أو افحص إحصاءات chunking دون فقدان البناء السابق.
- **Settings** — اختر مزود/نموذج embedding، معلمات chunking، و reranker لـ KB.

تُبنى الفهرسة على **LlamaIndex** من البداية إلى النهاية، مع إعادة فهرسة آمنة من الإعادة، اكتشاف عدم تطابق embedding، ومعالجة مرنة للمتجهات المستمرة الفاسدة.

### 🌐 Space — مكتبة التعلم الشخصية الخاصة بك

<div align="center">
<img src="../../assets/figs/dt-space.png" alt="Space" width="800">
</div>

Space هو نظير **القراءة / المراجعة** للأسطح النشطة. حيث تكون Chat / Co-Writer / Book هي حيث *تنتج*، فإن Space هو حيث يعيش كل ما تنتجه، قابلاً للبحث وإعادة التشغيل.

- **Chat History** — كل محادثة عبر كل وضع، مع إعادة تسمية العنوان، الحذف، والاستئناف.
- **Notebooks** — احفظ مخرجات من Chat و Research و Co-Writer في notebooks مصنفة ومرمزة بالألوان.
- **Question Bank** — كل سؤال اختبار مولد تلقائياً، قابل للتعليم بإشارة مرجعية و@-mention في الدردشة.
- **Skills** — ملفات `SKILL.md` ينشئها المستخدم وتحدد شخصيات تعليم (الاسم، الوصف، المحفزات، الجسم). عندما يكون skill نشطاً، يتم حقنه في prompt نظام الدردشة.

### 🧠 Memory — معمارية ثلاثية الطبقات

<div align="center">
<img src="../../assets/figs/dt-memory.png" alt="Memory Workbench" width="800">
</div>

ذاكرة DeepTutor الآن هي **خط أنابيب ثلاثي الطبقات** مع منضدة عمل قابلة للفحص في `/memory`.

| الطبقة | الدور | التخزين |
|:---|:---|:---|
| **L1 · مرآة مساحة العمل** (LIVE) | أثر إلحاق فقط لكل تفاعل، حسب السطح، حسب اليوم. السجل بدون فقدان لما حدث فعلاً. | `trace/<surface>/<YYYY-MM-DD>.jsonl` |
| **L2 · ملخصات حسب السطح** (CURATED) | حقائق خاصة بالسطح يستخرجها المُجمِّع. كل حقيقة تحمل اقتباسات حواشي تعود إلى آثار L1. | `L2/<surface>.md` |
| **L3 · معرفة عبر الأسطح** (SYNTHESIS) | توليف عبر الأسطح: `profile` الخاص بك، الخط الزمني `recent`، `scope` المعرفة، و `preferences`. ادعاءات محدَّدة، كل واحدة مدعومة بدليل L2. | `L3/<recent\|profile\|scope\|preferences>.md` |

سبعة أسطح تغذي خط الأنابيب: **chat, notebook, quiz, kb, book, tutorbot, cowriter**.

<div align="center">
<img src="../../assets/figs/dt-memgraph.png" alt="Memory Graph" width="800">
</div>

يصور **Memory Graph** (`/memory/graph`) جميع الطبقات الثلاث في وقت واحد: توليف L3 في المركز، حقائق L2 في الحلقة الوسطى، آثار L1 على الخارج، مجمَّعة حسب السطح.

### ⚙️ Settings — مركز تحكم موحد

<div align="center">
<img src="../../assets/figs/dt-settings.png" alt="Settings" width="800">
</div>

تم توحيد سطح الإعدادات في v1.4 وتقسيمه حسب الاهتمام، بنموذج مسودة / **Apply** حتى تكون التغييرات ذرية ويمكن التراجع عنها قبل الحفظ:

- **Appearance** — لغة الواجهة والسمة (Cream, Snow, Dark, Glass).
- **Status** — فحص صحة حي عبر LLM، embedding، البحث، وخلفيات التخزين.
- **LLM**، **Embedding**، **Search** — كاتالوج المزودين، عناوين URL الأساسية، مفاتيح API، واختيار النموذج النشط.
- **Capabilities** — قابلة للضبط لكل قدرة لـ Chat و Solve و Quiz و Research و Visualize و Co-Writer. مدعومة بمظروف `emit_capability_result` موحد و `UsageTracker` مشترك يكشف عن التكلفة لكل استدعاء.
- **Memory** — قم بتبديل تشغيلات المُجمِّع، قم بتكوين الإيقاع والميزانية، وانتقل إلى منضدة الذاكرة.
- **MCP servers** — سجل خوادم Model Context Protocol خارجية؛ تظهر أدواتها جنباً إلى جنب مع الأدوات المدمجة.
- **Tools** — افحص كل أداة مدمجة، معاملاتها، الحالة (مفعَّلة / قريباً)، وحالة نسخ i18n.

---

<a id="tutorbot"></a>
### 🦞 TutorBot — معلمو AI دائمون ومستقلون

<div align="center">
<img src="../../assets/figs/tutorbot-architecture.png" alt="TutorBot Architecture" width="800">
</div>

TutorBot ليس chatbot — إنه **وكيل دائم ومتعدد المثيلات** مبني على [nanobot](https://github.com/HKUDS/nanobot). يدير كل TutorBot حلقة الوكيل الخاصة به مع مساحة عمل، ذاكرة، وشخصية مستقلة.

<div align="center">
<img src="../../assets/figs/dt-tutorbot.png" alt="TutorBot Agents" width="800">
</div>

- **قوالب Soul** — حدد شخصية معلمك، نبرته، وفلسفته في التدريس من خلال ملفات Soul قابلة للتحرير.
- **مساحة عمل مستقلة** — لكل بوت دليله الخاص بذاكرة، جلسات، skills، وتكوين منفصل.
- **نبضات استباقية** — لا تستجيب البوتات فقط — بل تبادر. يتيح نظام Heartbeat المدمج فحوصات دراسية متكررة، تذكيرات بالمراجعة، ومهام مجدولة.
- **الوصول الكامل للأدوات** — كل بوت يصل إلى مجموعة أدوات DeepTutor الكاملة: استرداد RAG، تنفيذ الكود، البحث على الويب، البحث عن الأوراق الأكاديمية، التفكير العميق، والعصف الذهني.
- **تعلم Skills** — علّم بوتك قدرات جديدة بإضافة ملفات skills إلى مساحة عمله.
- **حضور متعدد القنوات** — اربط البوتات بـ Telegram و Discord و Slack و Feishu و WeChat Work و DingTalk و Matrix و QQ و WhatsApp و البريد الإلكتروني، والمزيد.
- **الفرق والوكلاء الفرعيون** — أنشئ وكلاء فرعيين في الخلفية أو نسّق فرق متعددة الوكلاء داخل بوت واحد.

```bash
deeptutor bot create math-tutor --persona "معلم رياضيات سقراطي يستخدم أسئلة استقصائية"
deeptutor bot create writing-coach --persona "مرشد كتابة صبور ومتأنٍ في التفاصيل"
deeptutor bot list                  # شاهد جميع معلميك النشطين
```

---

<a id="deeptutor-cli"></a>
### ⌨️ DeepTutor CLI — واجهة أصلية للوكلاء

<div align="center">
<img src="../../assets/figs/cli-architecture.png" alt="DeepTutor CLI Architecture" width="800">
</div>

DeepTutor أصلي تماماً لـ CLI. كل قدرة، قاعدة معرفة، جلسة، ذاكرة، و TutorBot على بعد أمر واحد — دون الحاجة لمتصفح.

**التنفيذ بأمر واحد**:

```bash
deeptutor run chat "اشرح تحويل فورييه" -t rag --kb textbook
deeptutor run deep_solve "أثبت أن √2 غير منطقي" -t reason
deeptutor run deep_question "الجبر الخطي" --config num_questions=5
deeptutor run deep_research "آليات الانتباه في transformers"
deeptutor run visualize "ارسم معمارية transformer"
```

**REPL تفاعلي**:

```bash
deeptutor chat --capability deep_solve --kb my-kb
# داخل REPL: /cap, /tool, /kb, /history, /notebook, /config للتبديل في الحال
```

**دورة حياة قاعدة المعرفة**:

```bash
deeptutor kb create my-kb --doc textbook.pdf
deeptutor kb add my-kb --docs-dir ./papers/
deeptutor kb search my-kb "الانحدار التدرجي"
deeptutor kb set-default my-kb
```

**وضع إخراج مزدوج**:

```bash
deeptutor run chat "لخص الفصل 3" -f rich    # إخراج ملوّن ومنسّق
deeptutor run chat "لخص الفصل 3" -f json    # أحداث JSON مفصولة بأسطر
```

**استمرارية الجلسة**:

```bash
deeptutor session list
deeptutor session open <id>
```

<details>
<summary><b>مرجع كامل لأوامر CLI</b></summary>

**المستوى الأعلى**

| الأمر | الوصف |
|:---|:---|
| `deeptutor run <capability> <message>` | تشغيل أي قدرة في دور واحد (`chat`, `deep_solve`, `deep_question`, `deep_research`, `math_animator`, `visualize`) |
| `deeptutor chat` | REPL تفاعلي مع `--capability`, `--tool`, `--kb`, `--language` اختيارية |
| `deeptutor serve` | بدء خادم DeepTutor API |

**`deeptutor bot`**

| الأمر | الوصف |
|:---|:---|
| `deeptutor bot list` | سرد جميع مثيلات TutorBot |
| `deeptutor bot create <id>` | إنشاء وبدء بوت جديد (`--name`, `--persona`, `--model`) |
| `deeptutor bot start <id>` | بدء بوت |
| `deeptutor bot stop <id>` | إيقاف بوت |

**`deeptutor kb`**

| الأمر | الوصف |
|:---|:---|
| `deeptutor kb list` | سرد جميع قواعد المعرفة |
| `deeptutor kb info <name>` | عرض تفاصيل قاعدة المعرفة |
| `deeptutor kb create <name>` | إنشاء من وثائق (`--doc`, `--docs-dir`) |
| `deeptutor kb add <name>` | إضافة وثائق بشكل تزايدي |
| `deeptutor kb search <name> <query>` | البحث في قاعدة معرفة |
| `deeptutor kb set-default <name>` | تعيين كـ KB افتراضية |
| `deeptutor kb delete <name>` | حذف قاعدة معرفة (`--force`) |

**`deeptutor memory`**

| الأمر | الوصف |
|:---|:---|
| `deeptutor memory show [file]` | عرض الذاكرة (`summary` أو `profile` أو `all`) |
| `deeptutor memory clear [file]` | مسح الذاكرة (`--force`) |

**`deeptutor session`**

| الأمر | الوصف |
|:---|:---|
| `deeptutor session list` | سرد الجلسات (`--limit`) |
| `deeptutor session show <id>` | عرض رسائل الجلسة |
| `deeptutor session open <id>` | استئناف الجلسة في REPL |
| `deeptutor session rename <id>` | إعادة تسمية جلسة (`--title`) |
| `deeptutor session delete <id>` | حذف جلسة |

**`deeptutor notebook`**

| الأمر | الوصف |
|:---|:---|
| `deeptutor notebook list` | سرد notebooks |
| `deeptutor notebook create <name>` | إنشاء notebook (`--description`) |
| `deeptutor notebook show <id>` | عرض سجلات notebook |
| `deeptutor notebook add-md <id> <path>` | استيراد markdown كسجل |
| `deeptutor notebook replace-md <id> <rec> <path>` | استبدال سجل markdown |
| `deeptutor notebook remove-record <id> <rec>` | إزالة سجل |

**`deeptutor book`**

| الأمر | الوصف |
|:---|:---|
| `deeptutor book list` | سرد جميع الكتب في مساحة العمل |
| `deeptutor book health <book_id>` | فحص انحراف KB وصحة الكتاب |
| `deeptutor book refresh-fingerprints <book_id>` | تحديث بصمات KB ومسح الصفحات القديمة |

**`deeptutor config` / `plugin` / `provider`**

| الأمر | الوصف |
|:---|:---|
| `deeptutor config show` | طباعة ملخص التكوين الحالي |
| `deeptutor plugin list` | سرد الأدوات والقدرات المسجلة |
| `deeptutor plugin info <name>` | عرض تفاصيل الأداة أو القدرة |
| `deeptutor provider login <provider>` | مصادقة المزود |

</details>

---

<a id="multi-user"></a>
### 👥 متعدد المستخدمين — نشر مشترك مع مساحات عمل لكل مستخدم

<div align="center">
<img src="../../assets/figs/dt-multi-user.png" alt="Multi-User" width="800">
</div>

فعّل المصادقة وسيتحول DeepTutor إلى نشر متعدد المستأجرين مع **مساحات عمل معزولة لكل مستخدم** و**موارد منسقة من المسؤول**. أول شخص يسجل يصبح المسؤول ويقوم بتكوين النماذج ومفاتيح API وقواعد المعرفة نيابة عن جميع الآخرين.

**بداية سريعة (5 خطوات):**

```bash
# 1. فعّل auth في data/user/settings/auth.json:
#    {"enabled": true, "token_expire_hours": 24, "cookie_secure": false}

# 2. أعد تشغيل حزمة الويب.
deeptutor start

# 3. افتح http://localhost:3782/register وأنشئ الحساب الأول.
#    التسجيل الأول هو الوحيد العام؛ يصبح هذا المستخدم admin
#    ويتم إغلاق نقطة النهاية /register تلقائياً بعد ذلك.

# 4. كـ admin، انتقل إلى /admin/users → "Add user" لإنشاء حسابات الزملاء.

# 5. لكل مستخدم، انقر على أيقونة شريط التمرير → عيّن ملفات LLM،
#    قواعد المعرفة، و skills. احفظ.
```

**ما يراه المسؤول:**

- **صفحة Settings كاملة** في `/settings` — إدارة مزودي LLM / embedding / البحث، مفاتيح API، كاتالوجات النماذج، و "Apply" وقت التشغيل.
- **إدارة المستخدمين** في `/admin/users` — إنشاء، ترقية، خفض، وحذف الحسابات.
- **محرر المنح** — لكل مستخدم غير admin، اختر ملفات النماذج، قواعد المعرفة، و skills التي يمكنهم استخدامها.
- **سجل التدقيق** — كل تغيير في المنح يُلحق بـ `multi-user/_system/audit/usage.jsonl`.

**ما يحصل عليه المستخدمون العاديون:**

- **مساحة عمل معزولة** تحت `multi-user/<uid>/` — تاريخ الدردشة الخاص بهم (`chat_history.db`)، الذاكرة، notebooks، وقواعد المعرفة الشخصية.
- **وصول للقراءة فقط** لقواعد المعرفة و skills التي عيّنها المسؤول.
- **صفحة Settings منقحة** — السمة، اللغة، وملخص النماذج الممنوحة فقط.
- **LLM ذو نطاق** — تمر أدوار الدردشة عبر النموذج المعيّن من المسؤول.

**بنية مساحة العمل:**

```
multi-user/
├── _system/
│   ├── auth/users.json          # بيانات اعتماد مجزأة، أدوار
│   ├── auth/auth_secret         # سر توقيع JWT (مولّد تلقائياً)
│   ├── grants/<uid>.json        # منح موارد لكل مستخدم (يديرها admin)
│   └── audit/usage.jsonl        # سجل التدقيق
└── <uid>/
    ├── user/
    │   ├── chat_history.db
    │   ├── settings/interface.json
    │   └── workspace/{chat,co-writer,book,...}
    ├── memory/{SUMMARY.md,PROFILE.md}
    └── knowledge_bases/...
```

**مرجع التكوين:**

| الإعداد | مطلوب | الوصف |
|:---|:---|:---|
| `data/user/settings/auth.json: enabled` | نعم | عيّن إلى `true` لتفعيل مصادقة متعددة المستخدمين. الافتراضي `false` (وضع المستخدم الواحد). |
| `multi-user/_system/auth/auth_secret` | موصى به | سر توقيع JWT. يُولَّد تلقائياً عند أول إقلاع مصادق إذا كان مفقوداً. |
| `data/user/settings/auth.json: token_expire_hours` | لا | عمر JWT؛ الافتراضي `24`. |
| `data/user/settings/auth.json: username/password_hash` | لا | بيانات اعتماد إقلاع اختيارية لمستخدم واحد بدون رأس. |
| `data/user/settings/system.json` | لا | يستنبط `deeptutor start` أعلام auth الواجهة الأمامية من إعدادات وقت التشغيل. |

> ⚠️ **وضع PocketBase (`integrations.pocketbase_url` معيّن) لمستخدم واحد فقط.** يجب أن تترك عمليات النشر متعددة المستخدمين `integrations.pocketbase_url` فارغة وتستخدم الخلفية الافتراضية JSON/SQLite.

> ⚠️ **توصية عملية واحدة.** ترقية أول مستخدم إلى admin محمية بـ `threading.Lock` داخل العملية. يجب على عمليات النشر متعددة العمال توفير admin الأول دون اتصال أو دعم متجر المستخدمين بنظام خارجي.

<a id="community"></a>
## 🌐 المجتمع والنظام البيئي

يقف DeepTutor على أكتاف مشاريع مفتوحة المصدر متميزة:

| المشروع | الدور في DeepTutor |
|:---|:---|
| [**nanobot**](https://github.com/HKUDS/nanobot) | محرك وكيل خفيف الوزن يشغّل TutorBot |
| [**LlamaIndex**](https://github.com/run-llama/llama_index) | خط أنابيب RAG والعمود الفقري لفهرسة الوثائق |
| [**ManimCat**](https://github.com/Wing900/ManimCat) | توليد رسوم متحركة رياضية بقيادة AI لـ Math Animator |

**من نظام HKUDS البيئي:**

| [⚡ LightRAG](https://github.com/HKUDS/LightRAG) | [🤖 AutoAgent](https://github.com/HKUDS/AutoAgent) | [🔬 AI-Researcher](https://github.com/HKUDS/AI-Researcher) | [🧬 nanobot](https://github.com/HKUDS/nanobot) |
|:---:|:---:|:---:|:---:|
| RAG بسيط وسريع | إطار وكلاء بدون كود | بحث آلي | وكيل AI خفيف الوزن |


## 🤝 المساهمة

<div align="center">

نأمل أن يصبح DeepTutor هدية للمجتمع. 🎁

<a href="https://github.com/HKUDS/DeepTutor/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HKUDS/DeepTutor&max=999" alt="Contributors" />
</a>

</div>

راجع [CONTRIBUTING.md](../../CONTRIBUTING.md) للحصول على إرشادات حول إعداد بيئة التطوير الخاصة بك، معايير الكود، وسير عمل pull request.

## ⭐ تاريخ النجوم

<div align="center">

<a href="https://www.star-history.com/#HKUDS/DeepTutor&type=timeline&legend=top-left">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&legend=top-left" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&legend=top-left" />
  </picture>
</a>

</div>

<p align="center">
 <a href="https://www.star-history.com/hkuds/deeptutor">
  <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/badge?repo=HKUDS/DeepTutor&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/badge?repo=HKUDS/DeepTutor" />
   <img alt="Star History Rank" src="https://api.star-history.com/badge?repo=HKUDS/DeepTutor" />
  </picture>
 </a>
</p>

<div align="center">

**[Data Intelligence Lab @ HKU](https://github.com/HKUDS)**

[⭐ نجّمنا](https://github.com/HKUDS/DeepTutor/stargazers) · [🐛 أبلغ عن خطأ](https://github.com/HKUDS/DeepTutor/issues) · [💬 المناقشات](https://github.com/HKUDS/DeepTutor/discussions)

---

مرخص بموجب [Apache License 2.0](../../LICENSE).

<p>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.DeepTutor&style=for-the-badge&color=00d4ff" alt="Views">
</p>

</div>
