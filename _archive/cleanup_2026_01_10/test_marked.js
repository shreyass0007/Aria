const marked = require('marked');

console.log('Marked version:', require('marked/package.json').version);

const text = `Sun Tzu, an ancient Chinese general, military strategist, and philosopher, is best known for his work "The Art of War." This treatise on military strategy and tactics is composed of 13 chapters, each dedicated to a different aspect of warfare. While the text offers numerous principles, here are five core rules or ideas that are frequently highlighted: 1. **The Importance of Strategy and Planning**: - Sun Tzu emphasizes the significance of careful planning and strategy before engaging in conflict. He believes that thorough preparation and understanding of both one's own strengths and weaknesses, as well as those of the enemy, are essential for victory. As he famously stated, "The supreme art of war is to subdue the enemy without fighting." 2. **Know Your Enemy and Yourself**: - One of Sun Tzu's central tenets is the idea of knowledge and intelligence. He advises that understanding your enemy's capabilities, intentions, and strategies, as well as having a clear awareness of your own, is crucial. This is encapsulated in his famous quote: "If you know the enemy and know yourself, you need not fear the result of a hundred battles." 3. **Adaptability and Flexibility**: - Sun Tzu stresses the importance of being adaptable and flexible in the face of changing circumstances. He advocates for leaders to be able to adjust their tactics and strategies in response to the battlefield's dynamic nature. As he puts it, "In the midst of chaos, there is also opportunity." 4. **The Value of Deception**: - Deception is a recurring theme in Sun Tzu's work. He argues that misleading the enemy about one's intentions and capabilities can provide a strategic advantage. This involves tactics such as feigning weakness when strong, and strength when weak. "All warfare is based on deception," he asserts. 5. **The Economy of Force**: - Sun Tzu advises against unnecessary action and advocates for the efficient use of resources. He believes in achieving objectives with the least amount of effort and expenditure. This principle is about maximizing effectiveness and minimizing waste, captured in his advice to "Appear at points which the enemy must hasten to defend; march swiftly to places where you are not expected." These rules reflect Sun Tzu's broader philosophy that winning wars is not just about brute force but about intelligence, strategy, and understanding the broader context of conflict. His teachings have been applied beyond military contexts, influencing fields like business, sports, and leadership.`;

try {
    marked.setOptions({
        breaks: true,
        gfm: true
    });

    const html = marked.parse(text);
    console.log('Parsing successful!');
    console.log('Preview:', html.substring(0, 200));
} catch (error) {
    console.error('Parsing failed:', error);
}
