# Test the cog_tutor package imports correctly
try:
    from cog_tutor import run_prompt
    print("SUCCESS: cog_tutor package imported correctly")
    print("The package is ready to use with your Qwen model.")
    print("\nTo test with a specific model, run:")
    print("  from cog_tutor import run_prompt")
    print("  output = run_prompt('item_explanation', {...}, model_id='your-model-id')")
    print("\nMake sure you have proper Hugging Face authentication if using gated models.")
except Exception as e:
    print(f"ERROR: Failed to import cog_tutor: {e}")
